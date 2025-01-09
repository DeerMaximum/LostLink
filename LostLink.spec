# -*- mode: python ; coding: utf-8 -*-
import site
import os

a = Analysis(
    ['main.py'],
    pathex=['lost_link'],
    binaries=[],
    datas=[],
    hiddenimports=['onnxruntime', 'sqlalchemy', 'args', 'posthog', 'hnswlib'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

#Change to your paths
lib_path = site.getsitepackages()[1]

a.datas += Tree(os.path.join(lib_path, "langchain"), prefix='langchain')
a.datas += Tree(os.path.join(lib_path, "llama_cpp"), prefix='llama_cpp')
a.datas += Tree(os.path.join(lib_path, "chromadb"), prefix='chromadb')
a.datas += Tree(os.path.join(lib_path, "pypika"), prefix='pypika')
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LostLink',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LostLink',
)
