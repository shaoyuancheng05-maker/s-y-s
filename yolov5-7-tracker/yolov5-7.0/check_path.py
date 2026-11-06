# -*- coding: utf-8 -*-
import os
# 检查 PATH 中各目录是否存在关键 DLL，以及版本
targets = ['msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll',
           'python3.dll', 'shiboken6.abi3.dll']
rows = []
for p in os.environ.get('PATH', '').split(';'):
    if not p or not os.path.isdir(p):
        continue
    for t in targets:
        fp = os.path.join(p, t)
        if os.path.exists(fp):
            try:
                import pefile
                pe = pefile.PE(fp, fast_load=True)
                ver = pe.VS_FIXEDFILEINFO
                v = ''
                pe.close()
            except Exception:
                v = ''
            sz = round(os.path.getsize(fp)/1024)
            rows.append(f"{t:22} {sz:5}KB  {p}")
txt = "\n".join(rows)
open(os.path.join(os.path.dirname(__file__), 'path_dlls.txt'), 'w', encoding='utf-8').write(txt)
print(txt)
