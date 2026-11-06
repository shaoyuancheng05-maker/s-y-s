# -*- coding: utf-8 -*-
"""诊断 Shiboken.pyd 的依赖：找缺失的 DLL 或缺失的导出函数。"""
import os, pefile, sys

ENV = sys.prefix
SHIBOKEN = os.path.join(ENV, 'Lib', 'site-packages', 'shiboken6', 'Shiboken.pyd')

# 模拟 DLL 搜索路径
search_dirs = [
    ENV,
    os.path.join(ENV, 'Library', 'bin'),
    os.path.join(ENV, 'DLLs'),
    r'C:\Windows\System32',
    r'C:\Windows\SysWOW64',
]
for p in os.environ.get('PATH', '').split(';'):
    if p and p not in search_dirs:
        search_dirs.append(p)


def find_dll(name):
    for d in search_dirs:
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
    except Exception as ex:
        return set()


def walk(path, depth=0, seen=None):
    if seen is None:
        seen = set()
    if path in seen or depth > 2:
        return
    seen.add(path)
    try:
        pe = pefile.PE(path, fast_load=True)
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
    except Exception as ex:
        print('  '*depth + '无法解析 ' + path + ': ' + str(ex))
        return
    if not hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
        return
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        dll = entry.dll.decode()
        found = find_dll(dll)
        if not found:
            print('  '*depth + f'[缺失DLL] {dll}  (被 {os.path.basename(path)} 引用)')
            continue
        # 检查函数
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
            print('  '*depth + f'[缺函数] {os.path.basename(path)} -> {dll} ({found})')
            for m in missing[:10]:
                print('  '*depth + '      缺少: ' + m)
        # 递归检查非系统DLL
        if 'Windows' not in found and depth < 2:
            walk(found, depth+1, seen)


print('=== 检查', SHIBOKEN, '===')
walk(SHIBOKEN)
print('诊断完成')
