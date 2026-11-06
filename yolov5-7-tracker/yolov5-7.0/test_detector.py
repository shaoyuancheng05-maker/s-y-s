# -*- coding: utf-8 -*-
import os, cv2, sys, glob, traceback
# 必须在 import yolov5 模块前设置，避免配置目录解析到 \tmp
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, '..', '..'))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
try:
    from detector import Detector
    det = Detector(os.path.join(ROOT, 'runs', 'train', 'exp4', 'weights', 'best.pt'),
                   os.path.join(ROOT, 'data', 'bvn.yaml'), device='0')
    print('模型加载成功, names:', det.names)
    tdir = os.path.join(PROJECT_ROOT, 'dataset', 'test')
    picked = None
    for f in sorted(glob.glob(os.path.join(tdir, '*.jpg'))):
        txt = f[:-4] + '.txt'
        if os.path.exists(txt) and os.path.getsize(txt) > 0:
            picked = f
            break
    print('测试图片:', os.path.basename(picked))
    img = cv2.imread(picked)
    out, res = det.predict(img)
    print('检测到', len(res), '个目标')
    for r in res:
        print('  ', r[5], round(r[4], 2), r[:4])
    cv2.imwrite(os.path.join(ROOT, 'gui_test.jpg'), out)
    print('保存测试图 OK')
except Exception:
    traceback.print_exc()
