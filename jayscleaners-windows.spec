# -*- mode: python -*-
from kivy.deps import sdl2, glew
block_cipher = None


a = Analysis(['c:\\users\\onedough83\\documents\\github\\jayscleaners-py\\main.py'],
             pathex=['C:\\Users\\onedough83\\Documents\\GitHub\\jayscleaners-py','C:\\Users\\onedough83\\Documents\\GitHub\\jayscleaners-py\\venv\\Scripts'],
             binaries=[('C:\\windows\\system32\\libusb0.dll','.')],
             datas=[( 'src/img/inventory', 'src/img/inventory' ), ('kv','kv'), ('components','components')],
             hiddenimports=['usb'],
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
          name='jayscleaners-windows',
          debug=False,
          bootloader_ignore_signals=True,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               name='jayscleaners-windows')
