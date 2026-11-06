# -*- coding: utf-8 -*-
import os, ctypes, traceback, sysconfig
shibdir = os.path.join(sysconfig.get_paths()['purelib'], 'shiboken6')
os.add_dll_directory(shibdir)

# 按依赖顺序，用绝对路径预加载 shibdir 自带的运行时（避免误用 PATH 里 latex 的旧版）
preload = ['vcruntime140.dll', 'vcruntime140_1.dll', 'msvcp140.dll',
           'msvcp140_1.dll', 'msvcp140_2.dll']
for d in preload:
    p = os.path.join(shibdir, d)
    if os.path.exists(p):
        ctypes.CDLL(p)
        print('预加载', d)

try:
    ctypes.CDLL(os.path.join(shibdir, 'shiboken6.abi3.dll'))
    print("abi3 加载成功!")
    from shiboken6 import Shiboken
    print("shiboken6 import 成功!")
    from PySide6.QtWidgets import QApplication
    print("PySide6 QtWidgets 成功!")
except Exception:
    traceback.print_exc()
