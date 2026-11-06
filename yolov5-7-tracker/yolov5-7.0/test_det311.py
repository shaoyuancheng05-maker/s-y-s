# -*- coding: utf-8 -*-
import os
import cv2
from detector import Detector

ROOT = os.path.dirname(os.path.abspath(__file__))
WEIGHTS = os.path.join(ROOT, 'runs', 'train', 'exp4', 'weights', 'best.pt')
YAML = os.path.join(ROOT, 'data', 'bvn.yaml')

det = Detector(WEIGHTS, YAML, conf_thres=0.25, device='0')
print('模型加载成功, 类别:', det.names)

# 找一张有标注的test图
test_dir = os.path.join(ROOT, '..', '..', 'dataset', 'test')
import glob
jpgs = sorted(glob.glob(os.path.join(test_dir, '*.jpg')))
# 找一个有非空标签的
pick = None
for j in jpgs:
    t = os.path.splitext(j)[0] + '.txt'
    if os.path.exists(t) and os.path.getsize(t) > 0:
        pick = j
        break
print('测试图:', pick)
img = cv2.imread(pick)
out, res = det.predict(img)
print('检出:', [(r[5], round(r[4], 2)) for r in res])
cv2.imwrite(os.path.join(ROOT, 'gui_test311.jpg'), out)
print('已保存 gui_test311.jpg')
