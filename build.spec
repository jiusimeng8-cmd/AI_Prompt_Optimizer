"""
PyInstaller 打包配置
运行: pyinstaller build.spec
"""

# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.ico', '.')],
    hiddenimports=[
        'keyboard._winkeyboard',
        'keyboard._generic',
        'win32api',
        'win32con',
        'win32gui',
        'ctypes',
        'uiautomation',
        'comtypes',
        'comtypes.client',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pandas',
        'numpy',
        'matplotlib',
        'scipy',
        'sklearn',
        'tensorflow',
        'torch',
        'PIL.ImageQt',
        'IPython',
        'jupyter',
        'notebook',
        'sqlalchemy',
        'openpyxl',
        'lxml',
        'regex',
        'transformers',
        'bcrypt',
        'nacl',
        'cryptography.hazmat.backends.openssl',
        'onnxruntime',
        'fsspec',
    ],
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
    name='AI_Prompt_Optimizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Windows图标
)
