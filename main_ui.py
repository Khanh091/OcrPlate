# main_ui.py
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def __init__(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 800)
        MainWindow.setStyleSheet("""
            QMainWindow {
                background-color: #f2f4f8;
            }
            QLabel {
                color: #222;
                background-color: white;
                border-radius: 10px;
                padding: 6px;
            }
            QLabel#text_header {
                background-color: #2f74c0;
                color: white;
                border-radius: 15px;
                padding: 10px;
            }
            QLabel#label_digits_in, QLabel#label_plate_in, QLabel#label_time_in, QLabel#label_status_in,
            QLabel#label_digits_out, QLabel#label_plate_out, QLabel#label_time_out, QLabel#label_status_out {
                border: 2px solid #2f74c0;
                font-weight: bold;
                color: #1c1c1c;
                background-color: #f8faff;
            }
            QPushButton {
                border-radius: 8px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton#btn_force_open_in {
                background-color: #1976d2;
                color: white;
            }
            QPushButton#btn_force_open_out {
                background-color: #1976d2;
                color: white;
            }
        """)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.text_header = QtWidgets.QLabel(self.centralwidget)
        self.text_header.setGeometry(QtCore.QRect(500, 10, 900, 60))
        font = QtGui.QFont("Segoe UI", 26, QtGui.QFont.Bold)
        self.text_header.setFont(font)
        self.text_header.setAlignment(QtCore.Qt.AlignCenter)
        self.text_header.setObjectName("text_header")

        self.label_main_in = QtWidgets.QLabel(self.centralwidget)
        self.label_main_in.setGeometry(QtCore.QRect(30, 90, 500, 375))
        self.label_main_in.setStyleSheet("border: 2px solid #333; background-color: #000;")
        self.label_main_in.setText("")
        self.label_main_in.setAlignment(QtCore.Qt.AlignCenter)
        self.label_main_in.setObjectName("label_main_in")

        self.label_main_out = QtWidgets.QLabel(self.centralwidget)
        self.label_main_out.setGeometry(QtCore.QRect(990, 90, 500, 375))
        self.label_main_out.setStyleSheet("border: 2px solid #333; background-color: #000;")
        self.label_main_out.setText("")
        self.label_main_out.setAlignment(QtCore.Qt.AlignCenter)
        self.label_main_out.setObjectName("label_main_out")

        self.label_plate_in = QtWidgets.QLabel(self.centralwidget)
        self.label_plate_in.setGeometry(QtCore.QRect(670, 100, 280, 100))
        font = QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold)
        self.label_plate_in.setFont(font)
        self.label_plate_in.setAlignment(QtCore.Qt.AlignCenter)
        self.label_plate_in.setObjectName("label_plate_in")

        self.label_digits_in = QtWidgets.QLabel(self.centralwidget)
        self.label_digits_in.setGeometry(QtCore.QRect(670, 210, 280, 70))
        self.label_digits_in.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold))
        self.label_digits_in.setAlignment(QtCore.Qt.AlignCenter)
        self.label_digits_in.setObjectName("label_digits_in")

        self.label_time_in = QtWidgets.QLabel(self.centralwidget)
        self.label_time_in.setGeometry(QtCore.QRect(670, 290, 280, 70))
        self.label_time_in.setFont(QtGui.QFont("Segoe UI", 12))
        self.label_time_in.setAlignment(QtCore.Qt.AlignCenter)
        self.label_time_in.setObjectName("label_time_in")

        self.label_status_in = QtWidgets.QLabel(self.centralwidget)
        self.label_status_in.setGeometry(QtCore.QRect(670, 370, 280, 70))
        self.label_status_in.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Bold))
        self.label_status_in.setAlignment(QtCore.Qt.AlignCenter)
        self.label_status_in.setWordWrap(True)
        self.label_status_in.setObjectName("label_status_in")

        self.label_plate_out = QtWidgets.QLabel(self.centralwidget)
        self.label_plate_out.setGeometry(QtCore.QRect(1630, 100, 280, 100))
        font = QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold)
        self.label_plate_out.setFont(font)
        self.label_plate_out.setAlignment(QtCore.Qt.AlignCenter)
        self.label_plate_out.setObjectName("label_plate_out")

        self.label_digits_out = QtWidgets.QLabel(self.centralwidget)
        self.label_digits_out.setGeometry(QtCore.QRect(1630, 210, 280, 70))
        self.label_digits_out.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold))
        self.label_digits_out.setAlignment(QtCore.Qt.AlignCenter)
        self.label_digits_out.setObjectName("label_digits_out")

        self.label_time_out = QtWidgets.QLabel(self.centralwidget)
        self.label_time_out.setGeometry(QtCore.QRect(1630, 290, 280, 70))
        self.label_time_out.setFont(QtGui.QFont("Segoe UI", 12))
        self.label_time_out.setAlignment(QtCore.Qt.AlignCenter)
        self.label_time_out.setObjectName("label_time_out")

        self.label_status_out = QtWidgets.QLabel(self.centralwidget)
        self.label_status_out.setGeometry(QtCore.QRect(1630, 370, 280, 70))
        self.label_status_out.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Bold))
        self.label_status_out.setAlignment(QtCore.Qt.AlignCenter)
        self.label_status_out.setWordWrap(True)
        self.label_status_out.setObjectName("label_status_out")

        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(50, 490, 220, 40))
        self.label_6.setFont(QtGui.QFont("Segoe UI", 15))
        self.label_6.setStyleSheet("background-color: none; border: none; color: #333;")
        self.label_6.setText("Trạng thái:")

        self.label_in = QtWidgets.QLabel(self.centralwidget)
        self.label_in.setGeometry(QtCore.QRect(30, 530, 500, 100))
        self.label_in.setStyleSheet("border: 2px solid #555; background-color: #eee;")
        self.label_in.setAlignment(QtCore.Qt.AlignCenter)
        self.label_in.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Bold))
        self.label_in.setWordWrap(True)
        self.label_in.setObjectName("label_in")

        self.btn_force_open_in = QtWidgets.QPushButton(self.centralwidget)
        self.btn_force_open_in.setGeometry(QtCore.QRect(190, 640, 200, 44))
        self.btn_force_open_in.setFont(QtGui.QFont("Segoe UI", 14, QtGui.QFont.Bold))
        self.btn_force_open_in.setObjectName("btn_force_open_in")
        self.btn_force_open_in.setText("Mở barrier")

        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(1010, 490, 220, 40))
        self.label_7.setFont(QtGui.QFont("Segoe UI", 15))
        self.label_7.setStyleSheet("background-color: none; border: none; color: #333;")
        self.label_7.setText("Trạng thái :")

        self.label_out = QtWidgets.QLabel(self.centralwidget)
        self.label_out.setGeometry(QtCore.QRect(990, 530, 500, 100))
        self.label_out.setStyleSheet("border: 2px solid #555; background-color: #eee;")
        self.label_out.setAlignment(QtCore.Qt.AlignCenter)
        self.label_out.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Bold))
        self.label_out.setWordWrap(True)
        self.label_out.setObjectName("label_out")

        self.btn_force_open_out = QtWidgets.QPushButton(self.centralwidget)
        self.btn_force_open_out.setGeometry(QtCore.QRect(1140, 640, 200, 44))
        self.btn_force_open_out.setFont(QtGui.QFont("Segoe UI", 14, QtGui.QFont.Bold))
        self.btn_force_open_out.setObjectName("btn_force_open_out")
        self.btn_force_open_out.setText("Mở barrier")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(540, 130, 120, 40))
        self.label.setFont(QtGui.QFont("Segoe UI", 12))
        self.label.setStyleSheet("background-color: none; border: none; color: #333;")
        self.label.setText("Biển số")

        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(540, 220, 120, 40))
        self.label_2.setFont(QtGui.QFont("Segoe UI", 12))
        self.label_2.setStyleSheet("background-color: none; border: none; color: #333;")
        self.label_2.setText("Đọc được")

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(540, 300, 120, 40))
        self.label_3.setFont(QtGui.QFont("Segoe UI", 12))
        self.label_3.setStyleSheet("background-color: none; border: none; color: #333;")
        self.label_3.setText("Thời gian")

        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(540, 380, 120, 40))
        self.label_5.setFont(QtGui.QFont("Segoe UI", 12))
        self.label_5.setStyleSheet("background-color: none; border: none; color: #333;")
        self.label_5.setText("Trạng thái")

        self.label_out_text = QtWidgets.QLabel(self.centralwidget)
        self.label_out_text.setGeometry(QtCore.QRect(1500, 130, 120, 40))
        self.label_out_text.setFont(QtGui.QFont("Segoe UI", 12))
        self.label_out_text.setStyleSheet("background-color: none; border: none; color: #333;")
        self.label_out_text.setText("Biển số")

        self.label_2_out = QtWidgets.QLabel(self.centralwidget)
        self.label_2_out.setGeometry(QtCore.QRect(1500, 220, 120, 40))
        self.label_2_out.setFont(QtGui.QFont("Segoe UI", 12))
        self.label_2_out.setStyleSheet("background-color: none; border: none; color: #333;")
        self.label_2_out.setText("Đọc được")

        self.label_3_out = QtWidgets.QLabel(self.centralwidget)
        self.label_3_out.setGeometry(QtCore.QRect(1500, 300, 120, 40))
        self.label_3_out.setFont(QtGui.QFont("Segoe UI", 12))
        self.label_3_out.setStyleSheet("background-color: none; border: none; color: #333;")
        self.label_3_out.setText("Thời gian")

        self.label_5_out = QtWidgets.QLabel(self.centralwidget)
        self.label_5_out.setGeometry(QtCore.QRect(1500, 380, 120, 40))
        self.label_5_out.setFont(QtGui.QFont("Segoe UI", 12))
        self.label_5_out.setStyleSheet("background-color: none; border: none; color: #333;")
        self.label_5_out.setText("Trạng thái")

        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setWindowTitle("Hệ thống nhận diện biển số")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.text_header.setText(_translate("MainWindow", "HỆ THỐNG NHẬN DIỆN BIỂN SỐ XE VÀO/RA"))
        self.label_plate_in.setText(_translate("MainWindow", "Không nhận thấy"))
        self.label_digits_in.setText(_translate("MainWindow", "Không nhận diện được"))
        self.label_time_in.setText(_translate("MainWindow", "Chưa có dữ liệu"))
        self.label_status_in.setText(_translate("MainWindow", "Đang xử lý..."))
        self.label_in.setText(_translate("MainWindow", "Chưa có thông tin barrier (vào)"))
        self.label_plate_out.setText(_translate("MainWindow", "Không nhận thấy"))
        self.label_digits_out.setText(_translate("MainWindow", "Không nhận diện được"))
        self.label_time_out.setText(_translate("MainWindow", "Chưa có dữ liệu"))
        self.label_status_out.setText(_translate("MainWindow", "Đang xử lý..."))
        self.label_out.setText(_translate("MainWindow", "Chưa có thông tin barrier (ra)"))
