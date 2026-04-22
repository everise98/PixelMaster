# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — run:  pyinstaller pixelrevive.spec

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/icon.ico', 'assets'),
        ('assets/models/realesr-general-x4v3.onnx', 'assets/models'),
        ('assets/models/RealESRGAN_x4plus.onnx', 'assets/models'),
    ],
    hiddenimports=[
        'PIL', 'PIL.Image', 'PIL.ImageFilter', 'PIL.ImageEnhance',
        'cv2', 'numpy',
        'PyQt6.QtCore', 'PyQt6.QtWidgets', 'PyQt6.QtGui', 'PyQt6.sip',
        'onnxruntime', 'onnxruntime.capi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'pandas', 'notebook', 'IPython',
        'torch', 'torchvision', 'basicsr', 'realesrgan', 'facexlib', 'gfpgan',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PixelMaster',
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
    icon='assets/icon.ico',
)
