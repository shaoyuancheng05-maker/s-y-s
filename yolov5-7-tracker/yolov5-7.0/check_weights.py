# -*- coding: utf-8 -*-
import os, time
ROOT = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(ROOT, 'runs', 'train')
out = []
for d in sorted(os.listdir(base)):
    p = os.path.join(base, d)
    w = os.path.join(p, 'weights')
    if os.path.isdir(w):
        for f in os.listdir(w):
            fp = os.path.join(w, f)
            mt = os.path.getmtime(fp)
            out.append(f"{d}/{f}  {round(os.path.getsize(fp)/1e6,1)}MB  {time.strftime('%m-%d %H:%M', time.localtime(mt))}")
    rf = os.path.join(p, 'results.csv')
    if os.path.exists(rf):
        n = len(open(rf, encoding='utf-8').read().strip().split('\n')) - 1
        out.append(f"   {d} 训练轮数: {n}")
txt = "\n".join(out)
open(os.path.join(ROOT, 'weights_info.txt'), 'w', encoding='utf-8').write(txt)
print(txt)
