import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

assets_dir = str(Path('.', 'assets').resolve())
if sys.platform == 'win32':
    icon_path = str(Path(assets_dir, 'icon.ico'))
else:
    icon_path = str(Path(assets_dir, 'icon.png'))

datas = []
datas += collect_data_files('PyQt6')
datas += collect_data_files('keyring')
datas.append((assets_dir, 'assets'))

hiddenimports = [
    'discord',
    'PyQt6',
    'keyring',
    'keyring.backends',
    'keyring.backends.SecretService',
    'keyring.backends.chainer',
]
hiddenimports += collect_submodules('keyring')

if sys.platform == 'win32':
    hiddenimports.append('keyring.backends.Windows')

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='disco-text',
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
    icon=icon_path,
)