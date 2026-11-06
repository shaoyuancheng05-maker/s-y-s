# -*- coding: utf-8 -*-
"""YOLOv5 检测封装：加载 best.pt，对视频帧做检测并画框。"""
import cv2
import numpy as np
import torch

from models.common import DetectMultiBackend
from utils.augmentations import letterbox
from utils.general import non_max_suppression, scale_boxes, check_img_size
from utils.torch_utils import select_device

# 三类违章框的颜色（BGR）
COLORS = {
    0: (0, 0, 255),       # wrong way：红色
    1: (180, 105, 255),   # no helmet：粉色
    2: (0, 165, 255),     # red_light_running：橙色
}

DISPLAY_NAMES = {
    0: 'wrong way',
    1: 'no helmet',
    2: 'red_light_running',
}


class Detector:
    def __init__(self, weights, data_yaml, imgsz=640, conf_thres=0.25,
                 iou_thres=0.45, device='', classes=None, display_names=None):
        self.device = select_device(device)
        self.model = DetectMultiBackend(weights, device=self.device,
                                        dnn=False, data=data_yaml)
        self.stride = self.model.stride
        self.names = self.model.names
        if isinstance(imgsz, int):
            imgsz = (imgsz, imgsz)
        self.imgsz = check_img_size(imgsz, s=self.stride)
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.classes = classes
        self.display_names = DISPLAY_NAMES if display_names is None else display_names
        # 预热
        self.model.warmup(imgsz=(1, 3, *self.imgsz))

    @torch.no_grad()
    def predict(self, img0, draw=True):
        """img0: BGR numpy 原图；返回 (画好框的 BGR 图, 检测结果列表)。"""
        # letterbox 缩放
        img = letterbox(img0, self.imgsz, stride=self.stride, auto=True)[0]
        img = img.transpose(2, 0, 1)[::-1]          # HWC BGR -> CHW RGB
        img = np.ascontiguousarray(img)
        im = torch.from_numpy(img).to(self.device)
        im = im.half() if self.model.fp16 else im.float()
        im /= 255.0
        if im.ndim == 3:
            im = im[None]
        pred = self.model(im, augment=False, visualize=False)
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres,
                                   classes=self.classes)
        det = pred[0]

        out = img0.copy() if draw else img0
        results = []
        if det is not None and len(det):
            det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], out.shape).round()
            for *xyxy, conf, cls in reversed(det):
                x1, y1, x2, y2 = [int(v) for v in xyxy]
                c = int(cls)
                name = self.display_names.get(c, self.names[c])
                results.append((x1, y1, x2, y2, float(conf), name))
                if not draw:
                    continue
                color = COLORS.get(c, (0, 255, 0))
                cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
                label = f"{name} {conf:.2f}"
                (tw, th), bl = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX,
                                               0.6, 2)
                ty = y1 - th - 6 if y1 - th - 6 > 0 else y1 + th + 6
                cv2.rectangle(out, (x1, ty - th - 4), (x1 + tw + 4, ty + 4),
                              color, -1)
                cv2.putText(out, label, (x1 + 2, ty),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255),
                            2, cv2.LINE_AA)
        return out, results
