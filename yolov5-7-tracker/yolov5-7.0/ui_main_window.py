# -*- coding: utf-8 -*-
"""主界面布局（对应报告第五章 main_window.ui 转换后的 ui_main_window.py）。"""
try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (QMainWindow, QWidget, QGridLayout, QLabel,
                                   QPushButton, QSlider)
except ModuleNotFoundError:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (QMainWindow, QWidget, QGridLayout, QLabel,
                                 QPushButton, QSlider)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("视频违章检测与车流量统计")
        MainWindow.resize(1100, 720)

        central = QWidget(MainWindow)
        MainWindow.setCentralWidget(central)
        grid = QGridLayout(central)
        grid.setContentsMargins(30, 20, 30, 20)
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(20)

        # 左侧：原始视频显示区
        self.input = QLabel()
        self.input.setAlignment(Qt.AlignCenter)
        self.input.setText("原始视频")
        self.input.setMinimumSize(480, 480)
        self.input.setStyleSheet("border:1px solid #999; background:#f0f0f0;")

        # 右侧：检测结果显示区
        self.output = QLabel()
        self.output.setAlignment(Qt.AlignCenter)
        self.output.setText("视频检测结果")
        self.output.setMinimumSize(480, 480)
        self.output.setStyleSheet("border:1px solid #999; background:#f0f0f0;")

        self.counter_status = QLabel("车流量：总数 0  |  向上 0  |  向下 0")
        self.counter_status.setAlignment(Qt.AlignCenter)
        self.counter_status.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.line_label = QLabel("计数线位置：65%（调整后重新计数）")
        self.line_slider = QSlider(Qt.Horizontal)
        self.line_slider.setRange(30, 85)
        self.line_slider.setValue(65)

        self.det_video = QPushButton("选择视频并开始检测")
        self.det_video.setMinimumHeight(70)

        grid.addWidget(self.input, 0, 0)
        grid.addWidget(self.output, 0, 1)
        grid.addWidget(self.counter_status, 1, 0, 1, 2)
        grid.addWidget(self.line_label, 2, 0)
        grid.addWidget(self.line_slider, 2, 1)
        grid.addWidget(self.det_video, 3, 0, 1, 2)
