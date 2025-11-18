import sys
from pathlib import Path
import torch
import cv2
import numpy as np

REPO_YOLOV5 = Path(__file__).resolve().parent / "yolov5"

class OcrPlate:
    def __init__(self, path_model_detect_plate, path_model_ocr, device='cpu'):
        self.device = device
        repo = str(REPO_YOLOV5) if REPO_YOLOV5.exists() else 'ultralytics/yolov5'
        self.model_license = torch.hub.load(repo_or_dir=repo, model='custom', path=path_model_detect_plate, source='local' if REPO_YOLOV5.exists() else 'github').to(self.device)
        self.model_ocr = torch.hub.load(repo_or_dir=repo, model='custom', path=path_model_ocr, source='local' if REPO_YOLOV5.exists() else 'github').to(self.device)

    def set_data(self, imgage_input):
        self.image_input = imgage_input.copy()
        self.image_output = imgage_input.copy()
        self.digit_out = 'unknow'
        self.box_xyxy = None
        self.detect_plate_ocr()

    def detect_plate_ocr(self):
        lbs = self.model_ocr.names
        img_bgr = self.image_input
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        results_plate = self.model_license(img_rgb)
        boxes_all = results_plate.xyxy[0].cpu().numpy() if len(results_plate.xyxy) > 0 else np.zeros((0,6))
        if boxes_all.size == 0:
            self.box_xyxy = np.zeros((0,4))
            return
        conf_mask = boxes_all[:,4] >= 0.8
        boxes = boxes_all[conf_mask][:,:4]
        self.box_xyxy = boxes
        for (x, y, x1, y1) in boxes.astype(int):
            x, y, x1, y1 = max(0, x), max(0, y), max(0, x1), max(0, y1)
            img_plate = self.image_input[y:y1, x:x1]
            if img_plate.size == 0:
                continue
            img_plate_rgb = cv2.cvtColor(img_plate, cv2.COLOR_BGR2RGB)
            res_ocr = self.model_ocr(img_plate_rgb)
            boxes_ocr = res_ocr.xyxy[0].cpu().numpy() if len(res_ocr.xyxy) > 0 else np.zeros((0,6))
            if boxes_ocr.size == 0:
                digit = 'unknow'
                cv2.putText(self.image_output, str(digit), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                cv2.rectangle(self.image_output, (x, y), (x1, y1), (0, 255, 0), 2)
                continue
            confs = boxes_ocr[:,4]
            mask_conf = confs >= 0.2
            boxes_ocr = boxes_ocr[mask_conf]
            len_digits = boxes_ocr.shape[0]
            digit = 'unknow'
            if (len_digits >= 7 and len_digits <= 10) and boxes_ocr[:,4].min() > 0.7:
                cls = boxes_ocr[:,5].astype(int).reshape(-1,1)
                x_center = (boxes_ocr[:,0] + boxes_ocr[:,2]) / 2.0
                y_center = (boxes_ocr[:,1] + boxes_ocr[:,3]) / 2.0
                xy_center = np.vstack([x_center, y_center]).T
                data = np.hstack([xy_center, cls])
                digit = self.process_ocr(data_center_labe=data, labels_encoder=lbs)
                self.digit_out = digit
            cv2.putText(self.image_output, str(digit), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
            cv2.rectangle(self.image_output, (x, y), (x1, y1), (0, 255, 0), 2)

    def process_ocr(self, data_center_labe: list, labels_encoder: dict):
        delta_y_max = np.max(data_center_labe[:,1]) - np.min(data_center_labe[:,1])
        out_ocr = None
        if delta_y_max > 30:
            y_mean = np.mean(data_center_labe[:,1])
            line1 = data_center_labe[data_center_labe[:,1] < y_mean]
            line2 = data_center_labe[data_center_labe[:,1] >= y_mean]
            line1 = line1[line1[:,0].argsort()]
            line2 = line2[line2[:,0].argsort()]
            out_ocr = ''.join([labels_encoder[int(item)] for item in line1[:,-1]])
            out_ocr += ' - ' + ''.join([labels_encoder[int(item)] for item in line2[:,-1]])
        else:
            data_center_labe = data_center_labe[data_center_labe[:,0].argsort()]
            out_ocr = ''.join([labels_encoder[int(item)] for item in data_center_labe[:,-1]])
            out_ocr = out_ocr[:3] + ' - ' + out_ocr[3:]
        return out_ocr
