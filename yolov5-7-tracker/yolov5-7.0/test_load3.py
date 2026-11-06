# -*- coding: utf-8 -*-
import os, ctypes, traceback, sys, sysconfig
shibdir = os.path.join(sysconfig.get_paths()['purelib'], 'shiboken6')
env = sys.prefix

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR = 0x00000100
LOAD_LIBRARY_SEARCH_DEFAULT_DIRS = 0x00001000
LOAD_LIBRARY_SEARCH_USER_DIRS = 0x00000400
LOAD_LIBRARY_SEARCH_APPLICATION_DIR = 0x00000200

# 添加 user dirs
os.add_dll_directory(shibdir)
os.add_dll_directory(env)

flags = (LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR | LOAD_LIBRARY_SEARCH_DEFAULT_DIRS
         | LOAD_LIBRARY_SEARCH_USER_DIRS)

def load_ex(path, tag):
    h = kernel32.LoadLibraryExW(path, None, flags)
    if not h:
        err = ctypes.get_last_error()
        print(f'{tag}: 失败 WinError {err}  {path}')
        return False
    print(f'{tag}: OK  {path}')
    return True

# 先严格加载依赖，再加载 abi3
for d in ['vcruntime140.dll', 'vcruntime140_1.dll', 'msvcp140.dll',
          'msvcp140_1.dll', 'msvcp140_2.dll']:
    load_ex(os.path.join(shibdir, d), 'dep')
load_ex(os.path.join(env, 'python3.dll'), 'python3')

if load_ex(os.path.join(shibdir, 'shiboken6.abi3.dll'), 'abi3'):
    try:
        from shiboken6 import Shiboken
        print("shiboken6 OK")
        from PySide6.QtWidgets import QApplication
        print("PySide6 OK")
    except Exception:
        traceback.print_exc()
