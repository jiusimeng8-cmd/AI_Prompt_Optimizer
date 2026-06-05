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
        'openai',
        'pydantic',
        'pydantic_core',
        'rich',
        'pygments',
        'PIL',
        'Pillow',
        'jiter',
        'distro',
        'sniffio',
        'websockets',
    ],
    noarchive=False,
    optimize=0,
)

# PyQt6 hooks tend to collect optional Qt components that this app does not use.
# Keep core widgets/platform/icon support, remove PDF/SVG/translation/software-OpenGL
# payloads to reduce the one-file executable without changing app logic.
def _is_optional_qt_payload(item):
    name = item[0].replace('\\', '/').lower()
    source = item[1].replace('\\', '/').lower() if len(item) > 1 else ''
    target = f"{name} {source}"

    optional_exact = (
        'opengl32sw.dll',
        'qt6pdf.dll',
        'qt6svg.dll',
        'qjpeg.dll',
        'qwebp.dll',
        'qtiff.dll',
    )
    if any(part in target for part in optional_exact):
        return True
    if '/translations/' in target and target.endswith('.qm'):
        return True
    return False


a.binaries = [item for item in a.binaries if not _is_optional_qt_payload(item)]
a.datas = [item for item in a.datas if not _is_optional_qt_payload(item)]

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
