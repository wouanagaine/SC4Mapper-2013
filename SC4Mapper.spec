# -*- mode: python -*-
a = Analysis(['SC4Map.py'],
             pathex=['L:\\SC4Mapper2'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\SC4Mapper', 'SC4Mapper.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'SC4Mapper'))
app = BUNDLE(coll,
             name=os.path.join('dist', 'SC4Mapper.app'))
