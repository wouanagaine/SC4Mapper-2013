python.exe -OO pyinstaller\pyinstaller.py -n SC4Mapper -w --upx-dir=upx308w SC4Map.py
python.exe -OO pyinstaller\pyinstaller.py -n SC4Mapper_debug -c --upx-dir=.\upx308w SC4Map.py
copy dist\sc4mapper_debug\sc4mapper_debug.* dist\sc4mapper
copy basicColors.ini dist\SC4Mapper
copy City*.sc4 dist\SC4Mapper
copy splash.jpg dist\SC4Mapper
md dist\SC4Mapper\doc
copy doc\*.* dist\SC4Mapper\doc
