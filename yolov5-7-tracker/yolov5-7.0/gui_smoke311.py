# -*- coding: utf-8 -*-
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# DLL 引导（与 main.py 相同）
import sysconfig
_purelib = sysconfig.get_paths()['purelib']
for _sub in ('PySide6', 'shiboken6'):
    _d = os.path.join(_purelib, _sub)
    if os.path.isdir(_d):
        os.add_dll_directory(_d)
os.add_dll_directory(os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System32'))

import cv2
from PySide6.QtWidgets import QApplication
from main import MainWindow, WEIGHTS, IMG_DIR

app = QApplication([])
win = MainWindow()
win.show()

# 直接加载模型（不等 singleShot）
win.load_model()
print('模型加载完成')

# 模拟一张图片检测
import glob
jpgs = sorted(glob.glob(os.path.join(IMG_DIR, '*.jpg')))
pick = None
for j in jpgs:
    t = os.path.splitext(j)[0] + '.txt'
    if os.path.exists(t) and os.path.getsize(t) > 0:
        pick = j
        break
img = cv2.imread(pick)
out, res = win.detector.predict(img)
print('GUI流程图片检测:', [(r[5], round(r[4], 2)) for r in res])
print('GUI 冒烟测试通过')
