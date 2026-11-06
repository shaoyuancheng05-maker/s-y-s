# -*- coding: utf-8 -*-
import os, ctypes, traceback, sysconfig
shibdir = os.path.join(sysconfig.get_paths()['purelib'], 'shiboken6')

# 方式1：用 add_dll_directory + 预加载 abi3
try:
    os.add_dll_directory(shibdir)
    abi = ctypes.CDLL(os.path.join(shibdir, 'shiboken6.abi3.dll'))
    print("abi3 预加载成功:", abi)
    from shiboken6 import Shiboken
    print("shiboken6 import 成功!")
    import PySide6
    from PySide6.QtWidgets import QApplication
    print("PySide6 QtWidgets 成功!")
except Exception:
    traceback.print_exc()
