# -*- coding: utf-8 -*-
"""诊断 Shiboken.pyd：优先在模块同目录找依赖，定位真正缺函数的 DLL。"""
import os, pefile, sys

ENV = sys.prefix
SHIBOKEN = os.path.join(ENV, 'Lib', 'site-packages', 'shiboken6', 'Shiboken.pyd')

base_dirs = [
    ENV,
    os.path.join(ENV, 'Library', 'bin'),
    os.path.join(ENV, 'DLLs'),
    r'C:\Windows\System32',
    r'C:\Windows\SysWOW64',
]
for p in os.environ.get('PATH', '').split(';'):
    if p and p not in base_dirs:
        base_dirs.append(p)


def find_dll(name, local_dir=None):
    # 先在引用模块同目录找
    if local_dir:
        cand = os.path.join(local_dir, name)
        if os.path.exists(cand):
            return cand
    for d in base_dirs:
        cand = os.path.join(d, name)
        if os.path.exists(cand):
            return cand
    return None


def get_exports(path):
    try:
        pe = pefile.PE(path, fast_load=True)
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
        names = set()
        if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
            for e in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                if e.name:
                    names.add(e.name.decode())
                else:
                    names.add(f"#{e.ordinal}")
        pe.close()
        return names
    except Exception:
        return set()


def walk(path, depth=0, seen=None):
    if seen is None:
        seen = set()
    if path in seen or depth > 3:
        return
    seen.add(path)
    local_dir = os.path.dirname(path)
    try:
        pe = pefile.PE(path, fast_load=True)
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
    except Exception as ex:
        print('  '*depth + '无法解析 ' + path + ': ' + str(ex))
        return
    if not hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
        pe.close()
        return
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        dll = entry.dll.decode()
        found = find_dll(dll, local_dir)
        if not found:
            print('  '*depth + f'[缺失DLL] {dll}  (被 {os.path.basename(path)} 引用)')
            continue
        exports = get_exports(found)
        missing = []
        for imp in entry.imports:
            if imp.name:
                if imp.name.decode() not in exports:
                    missing.append(imp.name.decode())
            else:
                if f"#{imp.ordinal}" not in exports:
                    missing.append(f"ordinal {imp.ordinal}")
        if missing:
            print('  '*depth + f'[缺函数] {os.path.basename(path)} -> {dll}')
            print('  '*depth + f'      实际DLL: {found}')
            for m in missing[:15]:
                print('  '*depth + '      缺少: ' + m)
        if 'Windows' not in found:
            walk(found, depth+1, seen)
    pe.close()


print('=== 检查', SHIBOKEN, '===')
walk(SHIBOKEN)
print('诊断完成')
