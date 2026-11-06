# -*- coding: utf-8 -*-
import os, pefile, sysconfig

shibdir = os.path.join(sysconfig.get_paths()['purelib'], 'shiboken6')
abi = os.path.join(shibdir, 'shiboken6.abi3.dll')

# api-set -> 实际DLL 映射
api_map = {
    'api-ms-win-crt-stdio-l1-1-0.dll': r'C:\Windows\System32\ucrtbase.dll',
    'api-ms-win-crt-string-l1-1-0.dll': r'C:\Windows\System32\ucrtbase.dll',
    'api-ms-win-crt-heap-l1-1-0.dll': r'C:\Windows\System32\ucrtbase.dll',
    'api-ms-win-crt-convert-l1-1-0.dll': r'C:\Windows\System32\ucrtbase.dll',
    'api-ms-win-crt-runtime-l1-1-0.dll': r'C:\Windows\System32\ucrtbase.dll',
    'api-ms-win-crt-math-l1-1-0.dll': r'C:\Windows\System32\ucrtbase.dll',
}

def exports(path):
    pe = pefile.PE(path, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
    s = set()
    if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
        for e in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            if e.name:
                s.add(e.name.decode())
    pe.close()
    return s

pe = pefile.PE(abi, fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
for e in pe.DIRECTORY_ENTRY_IMPORT:
    dll = e.dll.decode()
    funcs = [i.name.decode() if i.name else ('ord'+str(i.ordinal)) for i in e.imports]
    if dll.lower() == 'kernel32.dll':
        real = r'C:\Windows\System32\kernel32.dll'
        ex = exports(real)
        miss = [f for f in funcs if f not in ex]
        print(f'KERNEL32 {len(funcs)}函数, 缺失 {miss}')
        # 也查 kernelbase
        ex2 = exports(r'C:\Windows\System32\KernelBase.dll')
        miss2 = [f for f in funcs if f not in ex and f not in ex2]
        print(f'  合并kernelbase后仍缺: {miss2}')
    elif dll.lower().startswith('api-ms-win-crt'):
        real = api_map.get(dll.lower())
        ex = exports(real)
        miss = [f for f in funcs if f not in ex]
        print(f'{dll} {len(funcs)}函数 -> ucrtbase 缺失 {miss}')
pe.close()
print('完成')
