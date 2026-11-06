# -*- coding: utf-8 -*-
"""离屏冒烟测试：不弹窗，验证 GUI 创建、模型加载、图片检测流程。"""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import sys, glob, cv2, traceback
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, '..', '..'))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QCoreApplication
    app = QApplication(sys.argv)
    import main as m
    win = m.MainWindow()
    win.show()
    # 等待模型加载（singleShot 100ms）
    end = 0
    while win.detector is None and end < 100:
        app.processEvents()
        import time; time.sleep(0.1); end += 1
    print("模型加载完成:", win.detector is not None)
    # 模拟图片检测：挑3张有标注的图
    tdir = os.path.join(PROJECT_ROOT, 'dataset', 'test')
    files = [f for f in sorted(glob.glob(os.path.join(tdir, '*.jpg')))
             if os.path.getsize(f[:-4] + '.txt') > 0][:3]
    for f in files:
        img = cv2.imread(f)
        out, res = win.detector.predict(img)
        m.show_img(win.input, img)
        m.show_img(win.output, out)
        app.processEvents()
        print(os.path.basename(f), "检测到", len(res), "框:", [r[5] for r in res])
    print("GUI 冒烟测试通过")
except Exception:
    traceback.print_exc()
