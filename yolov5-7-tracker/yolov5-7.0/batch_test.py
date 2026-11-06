# -*- coding: utf-8 -*-
import os, cv2, sys, glob, traceback
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, '..', '..'))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
from detector import Detector

# 用较低置信度，看看模型能出多少框
for conf in (0.25, 0.10):
    det = Detector(os.path.join(ROOT, 'runs', 'train', 'exp4', 'weights', 'best.pt'),
                   os.path.join(ROOT, 'data', 'bvn.yaml'),
                   conf_thres=conf, device='0')
    tdir = os.path.join(PROJECT_ROOT, 'dataset', 'test')
    files = [f for f in sorted(glob.glob(os.path.join(tdir, '*.jpg')))
             if os.path.getsize(f[:-4] + '.txt') > 0]
    # 抽样前60张有标注的
    files = files[:60]
    cls_count = {}
    hit = 0
    total_box = 0
    for f in files:
        img = cv2.imread(f)
        _, res = det.predict(img)
        if res:
            hit += 1
        for r in res:
            total_box += 1
            cls_count[r[5]] = cls_count.get(r[5], 0) + 1
    print(f'--- conf={conf} 抽样{len(files)}张有标注图: 检出图{hit}张, 共{total_box}框, 分类{cls_count}')
