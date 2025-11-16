from main_ui import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
from OcrPlate import OcrPlate
from check_and_save_img import CheckAndSaveImg
import numpy as np
import sys
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from datetime import datetime
import ssl

# ================== Thông tin mô hình ==================
path_plate = 'model/best_plate.pt'
path_ocr = 'model/best_ocr.pt'

# ================== Cấu hình HiveMQ ==================
MQTT_BROKER = "03f372a29a8046d58d638f16d1c4d459.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "esp32"
MQTT_PASS = "espMQTT123"
MQTT_TOPIC_IN = "plate/read"
MQTT_TOPIC_OUT = "plate-out/read"

# Các topic barrier mới (theo yêu cầu)
MQTT_TOPIC_BARRIER_IN_OPEN = "barrier/cmd/open"
MQTT_TOPIC_BARRIER_IN_DENY = "barrier/cmd/deny"
MQTT_TOPIC_BARRIER_OUT_OPEN = "barrier-out/cmd/open"
MQTT_TOPIC_BARRIER_OUT_DENY = "barrier-out/cmd/deny"

# ================== Cấu hình MongoDB ==================
MONGO_URI = "mongodb+srv://nvkhanh0911_db_user:XFRLoocdSbSVXBQr@cluster0.9blxejx.mongodb.net/IoT_parking_system?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "IoT_parking_system"
COLLECTION_NAME = "vehicle_status"


# ================== Lớp chính ==================
class Main(Ui_MainWindow):
    def __init__(self, MainWindow):
        Ui_MainWindow.__init__(self, MainWindow=MainWindow)

        # --- Biến trạng thái topic barrier ---
        self.topic_barrier_in_open = False
        self.topic_barrier_in_deny = False
        self.topic_barrier_out_open = False
        self.topic_barrier_out_deny = False

        # --- Kết nối MQTT --- (đặt userdata=self để callback dễ lấy instance)
        self.mqtt_client = mqtt.Client(userdata=self)
        self.mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
        self.mqtt_client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
        self.mqtt_client.on_connect = self.on_connect_mqtt
        self.mqtt_client.on_message = self.on_message_mqtt
        self.mqtt_client.on_disconnect = self.on_disconnect
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            print("✅ Đã kết nối HiveMQ Cloud")
        except Exception as e:
            print("❌ Lỗi kết nối HiveMQ:", e)

        # --- Kết nối MongoDB ---
        try:
            self.mongo_client = MongoClient(MONGO_URI)
            self.db = self.mongo_client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            print("✅ Kết nối MongoDB thành công")
        except Exception as e:
            print("❌ Lỗi kết nối MongoDB:", e)

        # --- Khởi tạo camera vào ---
        self.cap_in = cv2.VideoCapture(2)
        if not self.cap_in.isOpened():
            print("❌ Không thể mở camera vào")
            return

        # --- Khởi tạo camera ra ---
        self.cap_out = cv2.VideoCapture(1)
        if not self.cap_out.isOpened():
            print("❌ Không thể mở camera ra")
            return

        # --- Đối tượng lưu và nhận diện ---
        self.OJ = CheckAndSaveImg()

        # --- Khởi tạo mô hình nhận dạng cho vào ---
        self.ocr_plate_in = OcrPlate(
            path_model_detect_plate=path_plate,
            path_model_ocr=path_ocr
        )

        # --- Khởi tạo mô hình nhận dạng cho ra ---
        self.ocr_plate_out = OcrPlate(
            path_model_detect_plate=path_plate,
            path_model_ocr=path_ocr
        )

        # --- Timer cho vào ---
        self.timer_in = QTimer()
        self.timer_in.start(8)
        self.timer_in.timeout.connect(self.start_predict_in)

        # --- Timer cho ra ---
        self.timer_out = QTimer()
        self.timer_out.start(8)
        self.timer_out.timeout.connect(self.start_predict_out)

        # --- Biến tạm cho vào ---
        self.digit_plate_in = None
        self.image_in_in = np.array([])
        self.last_sent_plate_in = ""

        # --- Biến tạm cho ra ---
        self.digit_plate_out = None
        self.image_in_out = np.array([])
        self.last_sent_plate_out = ""

        # --- Kết nối UI buttons ---
        try:
            self.btn_force_open_in.clicked.connect(self.force_open_in)
            self.btn_force_open_out.clicked.connect(self.force_open_out)
        except Exception:
            # nếu UI không có nút (phiên bản cũ) thì bỏ qua
            pass

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("❗ MQTT disconnected unexpectedly. Reconnecting...")
            try:
                client.reconnect()
            except Exception as e:
                print("❌ Reconnect failed:", e)

    # ================== MQTT callbacks ==================
    def on_connect_mqtt(self, client, userdata, flags, rc):
        if rc == 0:
            print("🔌 MQTT connected, subscribing to barrier topics...")
            try:
                client.subscribe(MQTT_TOPIC_BARRIER_IN_OPEN)
                client.subscribe(MQTT_TOPIC_BARRIER_IN_DENY)
                client.subscribe(MQTT_TOPIC_BARRIER_OUT_OPEN)
                client.subscribe(MQTT_TOPIC_BARRIER_OUT_DENY)
                print("📥 Subscribed to barrier topics.")
            except Exception as e:
                print("❌ Subscribe failed:", e)
        else:
            print("❌ MQTT connect returned code", rc)

    def on_message_mqtt(self, client, userdata, msg):
        try:
            main = userdata  # userdata là instance Main (khi tạo client userdata=self)
        except Exception:
            main = None

        topic = msg.topic
        payload = msg.payload.decode(errors='ignore') if msg.payload is not None else ""

        # Cập nhật cờ trạng thái dựa trên topic
        if main:
            if topic == MQTT_TOPIC_BARRIER_IN_OPEN:
                main.topic_barrier_in_open = True
                main.topic_barrier_in_deny = False
                print("➡️ Received barrier in OPEN:", payload)
            elif topic == MQTT_TOPIC_BARRIER_IN_DENY:
                main.topic_barrier_in_deny = True
                main.topic_barrier_in_open = False
                print("➡️ Received barrier in DENY:", payload)
            elif topic == MQTT_TOPIC_BARRIER_OUT_OPEN:
                main.topic_barrier_out_open = True
                main.topic_barrier_out_deny = False
                print("➡️ Received barrier out OPEN:", payload)
            elif topic == MQTT_TOPIC_BARRIER_OUT_DENY:
                main.topic_barrier_out_deny = True
                main.topic_barrier_out_open = False
                print("➡️ Received barrier out DENY:", payload)
            else:
                pass

    # ================== Force open từ UI (publish) ==================
    def force_open_in(self):
        try:
            self.mqtt_client.publish(MQTT_TOPIC_BARRIER_IN_OPEN, "force_open")
            self.topic_barrier_in_open = True
            self.topic_barrier_in_deny = False
            self.label_in.setText("Yêu cầu mở (force_open) đã gửi")
            self.label_in.setStyleSheet("border: 2px solid #4caf50; background-color: #eaf8ea;")
            print("📤 Sent force_open to", MQTT_TOPIC_BARRIER_IN_OPEN)
        except Exception as e:
            print("❌ Lỗi khi gửi force_open (vào):", e)
            self.label_in.setText("Gửi force_open thất bại")
            self.label_in.setStyleSheet("border: 2px solid #f44336; background-color: #fdecea;")

    def force_open_out(self):
        try:
            self.mqtt_client.publish(MQTT_TOPIC_BARRIER_OUT_OPEN, "force_open")
            self.topic_barrier_out_open = True
            self.topic_barrier_out_deny = False
            self.label_out.setText("Yêu cầu mở (force_open) đã gửi")
            self.label_out.setStyleSheet("border: 2px solid #4caf50; background-color: #eaf8ea;")
            print("📤 Sent force_open to", MQTT_TOPIC_BARRIER_OUT_OPEN)
        except Exception as e:
            print("❌ Lỗi khi gửi force_open (ra):", e)
            self.label_out.setText("Gửi force_open thất bại")
            self.label_out.setStyleSheet("border: 2px solid #f44336; background-color: #fdecea;")

    # ================== Cập nhật nhãn trạng thái barrier lên UI (gọi thường xuyên) ==================
    def update_barrier_labels(self):
        try:
            # Vào (entry)
            if self.topic_barrier_in_open:
                self.label_in.setText("Còn chỗ — Mở barrier")
                self.label_in.setStyleSheet("border: 2px solid #4caf50; background-color: #eaf8ea;")
            elif self.topic_barrier_in_deny:
                self.label_in.setText("Bãi đỗ hết chỗ")
                self.label_in.setStyleSheet("border: 2px solid #f44336; background-color: #fdecea;")
            else:
                self.label_in.setText("Chưa có thông tin barrier (vào)")
                self.label_in.setStyleSheet("border: 2px solid #555; background-color: #eee;")

            # Ra (exit)
            if self.topic_barrier_out_open:
                self.label_out.setText("Thông tin thẻ và xe hợp lệ — Mời ra")
                self.label_out.setStyleSheet("border: 2px solid #4caf50; background-color: #eaf8ea;")
            elif self.topic_barrier_out_deny:
                self.label_out.setText("Thông tin thẻ và xe không hợp lệ")
                self.label_out.setStyleSheet("border: 2px solid #f44336; background-color: #fdecea;")
            else:
                self.label_out.setText("Thông tin thẻ và xe không hợp lệ")
                self.label_out.setStyleSheet("border: 2px solid #555; background-color: #eee;")
        except Exception as e:
            print("⚠️ Lỗi khi cập nhật label barrier:", e)

    # ================== Xử lý khung hình vào ==================
    def start_predict_in(self):
        try:
            ret, frame = self.cap_in.read()
            if not ret or frame is None:
                # vẫn cập nhật trạng thái barrier dù camera lỗi
                self.update_barrier_labels()
                return

            # Hiển thị frame gốc để debug camera
            frame_main_raw = self.convert_qimg(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.label_main_in.setPixmap(
                QPixmap.fromImage(frame_main_raw).scaled(self.label_main_in.size())
            )

            frame_in = frame.copy()
            self.ocr_plate_in.set_data(frame)

            if getattr(self.ocr_plate_in, "image_output", None) is None:
                self.update_barrier_labels()
                return

            frame_main = self.convert_qimg(
                cv2.cvtColor(self.ocr_plate_in.image_output, cv2.COLOR_BGR2RGB)
            )

            digits = self.ocr_plate_in.digit_out

            # Nếu nhận diện được biển số
            if digits != 'unknow':
                self.digit_plate_in = digits
                self.image_in_in = self.ocr_plate_in.image_input

                # Gửi MQTT nếu là biển mới
                if digits != self.last_sent_plate_in:
                    try:
                        self.mqtt_client.publish(MQTT_TOPIC_IN, digits)
                        print(f"📤 Đã gửi biển số mới lên HiveMQ (vào): {digits}")
                        self.last_sent_plate_in = digits
                        if digits == self.last_sent_plate_out:
                            self.last_sent_plate_out = ""
                    except Exception as e:
                        print("❌ Lỗi khi gửi MQTT (vào):", e)

                # Hiển thị ảnh biển nhỏ (vẫn giữ label_plate_in)
                if hasattr(self.ocr_plate_in, "box_xyxy") and len(self.ocr_plate_in.box_xyxy) > 0:
                    xyxy = self.ocr_plate_in.box_xyxy[-1]
                    x, y, x1, y1 = map(int, xyxy)
                    frame_cut = frame_in[y:y1, x:x1]
                    frame_plate = self.convert_qimg(cv2.cvtColor(frame_cut, cv2.COLOR_BGR2RGB))
                    self.label_plate_in.setPixmap(
                        QPixmap.fromImage(frame_plate).scaled(self.label_plate_in.size())
                    )

                # Truy vấn trạng thái từ MongoDB
                vehicle = self.collection.find_one({"plate": digits})
                if vehicle:
                    status = vehicle.get("status", "Không rõ")
                    time_in = vehicle.get("time_in")
                    time_out = vehicle.get("time_out")

                    self.label_status_in.setText(status)

                    # Hiển thị thời gian vào
                    if time_in:
                        try:
                            if isinstance(time_in, dict) and "$date" in time_in:
                                time_in_value = int(time_in["$date"]["$numberLong"]) / 1000
                                time_in_str = datetime.fromtimestamp(time_in_value).strftime("%H:%M:%S %d-%m-%Y")
                            else:
                                time_in_str = str(time_in)
                            self.label_time_in.setText(time_in_str)
                        except Exception:
                            self.label_time_in.setText("Lỗi thời gian")
                    else:
                        self.label_time_in.setText("Chưa vào")
                else:
                    self.label_status_in.setText("Xe chưa vào bãi")
                    self.label_time_in.setText("Không có thời gian")

                self.label_digits_in.setText(f'{str(digits)}')

            # Nếu KHÔNG nhận diện được
            else:
                self.digit_plate_in = None
                self.image_in_in = np.array([])

                self.label_plate_in.setText('Không nhận thấy')
                self.label_digits_in.setText('Không nhận diện được')
                self.label_time_in.setText('Không nhận dạng được')
                self.label_status_in.setText('Không nhận dạng được')

            # Hiển thị hình camera chính
            self.label_main_in.setPixmap(
                QPixmap.fromImage(frame_main).scaled(self.label_main_in.size())
            )

            # Cập nhật trạng thái barrier (không liên quan tới ảnh)
            self.update_barrier_labels()

        except Exception as e:
            print("⚠️ Lỗi trong quá trình xử lý khung hình vào:", e)

    # ================== Xử lý khung hình ra ==================
    def start_predict_out(self):
        try:
            ret, frame = self.cap_out.read()
            if not ret or frame is None:
                self.update_barrier_labels()
                return

            # Hiển thị frame gốc để debug camera
            frame_main_raw = self.convert_qimg(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.label_main_out.setPixmap(
                QPixmap.fromImage(frame_main_raw).scaled(self.label_main_out.size())
            )

            frame_in = frame.copy()
            self.ocr_plate_out.set_data(frame)

            if getattr(self.ocr_plate_out, "image_output", None) is None:
                self.update_barrier_labels()
                return

            frame_main = self.convert_qimg(
                cv2.cvtColor(self.ocr_plate_out.image_output, cv2.COLOR_BGR2RGB)
            )

            digits = self.ocr_plate_out.digit_out

            # Nếu nhận diện được biển số
            if digits != 'unknow':
                self.digit_plate_out = digits
                self.image_in_out = self.ocr_plate_out.image_input

                # Gửi MQTT nếu là biển mới
                if digits != self.last_sent_plate_out:
                    try:
                        self.mqtt_client.publish(MQTT_TOPIC_OUT, digits)
                        print(f"📤 Đã gửi biển số mới lên HiveMQ (ra): {digits}")
                        self.last_sent_plate_out = digits

                        if digits == self.last_sent_plate_in:
                            self.last_sent_plate_in = ""
                    except Exception as e:
                        print("❌ Lỗi khi gửi MQTT (ra):", e)

                # Hiển thị ảnh biển nhỏ
                if hasattr(self.ocr_plate_out, "box_xyxy") and len(self.ocr_plate_out.box_xyxy) > 0:
                    xyxy = self.ocr_plate_out.box_xyxy[-1]
                    x, y, x1, y1 = map(int, xyxy)
                    frame_cut = frame_in[y:y1, x:x1]
                    frame_plate = self.convert_qimg(cv2.cvtColor(frame_cut, cv2.COLOR_BGR2RGB))
                    self.label_plate_out.setPixmap(
                        QPixmap.fromImage(frame_plate).scaled(self.label_plate_out.size())
                    )

                # Truy vấn trạng thái từ MongoDB
                vehicle = self.collection.find_one({"plate": digits})
                if vehicle:
                    status = vehicle.get("status", "Không rõ")
                    time_in = vehicle.get("time_in")
                    time_out = vehicle.get("time_out")

                    self.label_status_out.setText(status)

                    # Hiển thị thời gian ra
                    if time_out:
                        try:
                            if isinstance(time_out, dict) and "$date" in time_out:
                                time_out_value = int(time_out["$date"]["$numberLong"]) / 1000
                                time_out_str = datetime.fromtimestamp(time_out_value).strftime("%H:%M:%S %d-%m-%Y")
                            else:
                                time_out_str = str(time_out)
                            self.label_time_out.setText(time_out_str)
                        except Exception:
                            self.label_time_out.setText("Lỗi thời gian")
                    else:
                        self.label_time_out.setText("Chưa ra")
                else:
                    self.label_status_out.setText("Xe chưa vào bãi")
                    self.label_time_out.setText("Không có thời gian")

                self.label_digits_out.setText(f'{str(digits)}')

            # Nếu KHÔNG nhận diện được
            else:
                self.digit_plate_out = None
                self.image_in_out = np.array([])

                self.label_plate_out.setText('Không nhận thấy')
                self.label_digits_out.setText('Không nhận diện được')
                self.label_time_out.setText('Không nhận dạng được')
                self.label_status_out.setText('Không nhận dạng được')

            # Hiển thị hình camera chính
            self.label_main_out.setPixmap(
                QPixmap.fromImage(frame_main).scaled(self.label_main_out.size())
            )

            # Cập nhật trạng thái barrier
            self.update_barrier_labels()

        except Exception as e:
            print("⚠️ Lỗi trong quá trình xử lý khung hình ra:", e)

    # ================== Khi đóng ứng dụng ==================
    def closeEvent(self, event):
        if self.cap_in.isOpened():
            self.cap_in.release()
        if self.cap_out.isOpened():
            self.cap_out.release()
        self.timer_in.stop()
        self.timer_out.stop()
        try:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        except Exception:
            pass
        try:
            self.mongo_client.close()
        except Exception:
            pass
        print("🛑 Đã ngắt kết nối và dừng chương trình.")
        event.accept()

    # ================== Chuyển numpy -> QImage ==================
    def convert_qimg(self, image):
        try:
            h, w, ch = image.shape
            bytes_per_line = ch * w
            res = QImage(image.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
            return res
        except Exception as e:
            print("⚠️ Lỗi khi chuyển đổi QImage:", e)
            return QImage()


# ================== Chạy ứng dụng ==================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Main(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
