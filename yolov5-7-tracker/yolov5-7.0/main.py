

import os


import sys
import cv2
try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QImage, QPixmap
    from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
except ModuleNotFoundError:
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QImage, QPixmap
    from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

from ui_main_window import Ui_MainWindow
from detector import Detector
from vehicle_counter import VEHICLE_CLASSES, VehicleCounter

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, '..', '..'))
WEIGHTS = os.path.join(ROOT, 'runs', 'train', 'exp4', 'weights', 'best.pt')
DATA_YAML = os.path.join(ROOT, 'data', 'bvn.yaml')
VEHICLE_WEIGHTS = os.path.join(ROOT, 'yolov5s.pt')
COCO_YAML = os.path.join(ROOT, 'data', 'coco128.yaml')
VIDEO_FILE = os.path.join(PROJECT_ROOT, 'VID_20251028_083623.mp4')


def cv2qimage(img):
    """BGR numpy -> QImage。"""
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, c = rgb.shape
    qimg = QImage(rgb.data, w, h, c * w, QImage.Format_RGB888)
    return qimg.copy()


def show_img(label, img):
    """把 BGR 图按比例缩放显示到 QLabel。"""
    pix = QPixmap.fromImage(cv2qimage(img))
    pix = pix.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
    label.setPixmap(pix)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.detector = None
        self.vehicle_detector = None
        self.vehicle_counter = VehicleCounter()
        self.video = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.video_pred)
        self.det_video.clicked.connect(self.open_video)
        self.det_video.setEnabled(False)
        self.line_slider.valueChanged.connect(self.change_count_line)
        # 界面先显示，再加载模型
        QTimer.singleShot(100, self.load_model)

    def load_model(self):
        self.output.setText("模型加载中，请稍候...")
        QApplication.processEvents()
        self.detector = Detector(WEIGHTS, DATA_YAML, conf_thres=0.25, device='')
        self.vehicle_detector = Detector(VEHICLE_WEIGHTS, COCO_YAML,
                                        conf_thres=0.30, device='',
                                        classes=VEHICLE_CLASSES, display_names={})
        self.output.setText("视频检测结果")
        self.det_video.setEnabled(True)

    def update_count_label(self):
        counter = self.vehicle_counter
        self.counter_status.setText("车流量：总数 {}  |  向上 {}  |  向下 {}".format(
            counter.total, counter.up, counter.down))

    def change_count_line(self, value):
        self.vehicle_counter.line_fraction = value / 100
        self.vehicle_counter.reset()
        self.line_label.setText("计数线位置：{}%（调整后重新计数）".format(value))
        self.update_count_label()

    # ---------- 视频检测 ----------
    def open_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频", VIDEO_FILE, "视频文件 (*.mp4 *.avi *.mov *.mkv)")
        if file_path:
            video = cv2.VideoCapture(file_path)
            if not video.isOpened():
                self.output.setText("无法打开视频：{}".format(file_path))
                return
            self.timer.stop()
            if self.video is not None:
                self.video.release()
            self.video = video
            self.vehicle_counter.reset()
            self.update_count_label()
            self.timer.start(30)

    def video_pred(self):
        ret, frame = self.video.read()
        if not ret:
            self.timer.stop()
            self.video.release()
            self.video = None
            return
        out, _ = self.detector.predict(frame)
        _, vehicles = self.vehicle_detector.predict(frame, draw=False)
        visible = self.vehicle_counter.update(vehicles, frame.shape)
        self.vehicle_counter.draw(out, visible)
        self.update_count_label()
        show_img(self.input, frame)
        show_img(self.output, out)

    def closeEvent(self, event):
        self.timer.stop()
        if self.video is not None:
            self.video.release()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
