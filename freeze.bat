py -3.5 C:\Python35\Scripts\cxfreeze arky-cli.py -OO --compress --target-dir=downloads/arky-cli-amd64 --icon=ark.ico
C:\Users\Bruno\upx.exe --best downloads\arky-cli-amd64\python*.dll
C:\Users\Bruno\upx.exe --best downloads\arky-cli-amd64\*.pyd
py -3.5-32 C:\Python35\Scripts\cxfreeze arky-cli.py -OO --compress --target-dir=downloads/arky-cli-win32 --icon=ark.ico
C:\Users\Bruno\upx.exe --best downloads\arky-cli-win32\python*.dll
C:\Users\Bruno\upx.exe --best downloads\arky-cli-win32\*.pyd
