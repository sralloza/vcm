# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
options = [ ('v', None, 'OPTION')]

a = Analysis(['cli.py'],
             pathex=['D:\\.scripts\\vcm'],
             binaries=[],
             datas=[("vcm/VERSION", "vcm/"), ("vcm/notifier/base64.json", "vcm/notifier/")],
             hiddenimports=["toml"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='vcm',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='vcm')
