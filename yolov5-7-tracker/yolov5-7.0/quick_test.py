# -*- coding: utf-8 -*-
import os, cv2, sys, glob
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, '..', '..'))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
from detector import Detector

det = Detector(os.path.join(ROOT, 'runs', 'train', 'exp4', 'weights', 'best.pt'),
               os.path.join(ROOT, 'data', 'bvn.yaml'),
               conf_thres=0.25, device='0')
tdir = os.path.join(PROJECT_ROOT, 'dataset', 'test')
files = [f for f in sorted(glob.glob(os.path.join(tdir, '*.jpg')))
         if os.path.getsize(f[:-4] + '.txt') > 0]
cls = {}
hit = 0
for f in files:
    img = cv2.imread(f)
    out, res = det.predict(img)
    if res:
        hit += 1
    for r in res:
        cls[r[5]] = cls.get(r[5], 0) + 1
print(f'exp4 conf=0.25: {len(files)}张有标注图, 检出{hit}张, 分类统计{cls}')
