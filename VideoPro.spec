import os
import sys
from PyInstaller.utils.hooks import collect_all

import customtkinter
ctk_path = os.path.dirname(customtkinter.__file__)

# Collect all for imageio and moviepy as they often have metadata issues in PyInstaller
imageio_datas, imageio_binaries, imageio_hiddenimports = collect_all('imageio')
moviepy_datas, moviepy_binaries, moviepy_hiddenimports = collect_all('moviepy')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=imageio_binaries + moviepy_binaries,
    datas=[(ctk_path, 'customtkinter/')] + imageio_datas + moviepy_datas,
    hiddenimports=imageio_hiddenimports + moviepy_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VideoPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
