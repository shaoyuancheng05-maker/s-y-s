# -*- coding: utf-8 -*-
import os, ctypes, traceback, sys, sysconfig
shibdir = os.path.join(sysconfig.get_paths()['purelib'], 'shiboken6')
env = sys.prefix

# 逐个用绝对路径加载 abi3 的依赖
candidates = [
    ('MSVCP140(shib)', os.path.join(shibdir, 'msvcp140.dll')),
    ('MSVCP140(env)', os.path.join(env, 'msvcp140.dll')),
    ('VCRUNTIME140(shib)', os.path.join(shibdir, 'vcruntime140.dll')),
    ('VCRUNTIME140_1(shib)', os.path.join(shibdir, 'vcruntime140_1.dll')),
    ('VCRUNTIME140_1(env)', os.path.join(env, 'vcruntime140_1.dll')),
    ('python3(env)', os.path.join(env, 'python3.dll')),
]
for name, path in candidates:
    if not os.path.exists(path):
        print(name, '文件不存在')
        continue
    try:
        h = ctypes.CDLL(path)
        print(f'{name:24} OK   {path}')
    except OSError as e:
        print(f'{name:24} 失败 {e}   {path}')
