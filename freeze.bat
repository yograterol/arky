py -3.5 C:\Python35\Scripts\cxfreeze arky-cli.py -OO --compress --target-dir=arky-cli-amd64 --icon=ark.ico
C:\Users\Bruno\upx.exe --best arky-cli.amd64\python*.dll
C:\Users\Bruno\upx.exe --best arky-cli.amd64\*.pyd
py -3.5-32 C:\Python35\Scripts\cxfreeze arky-cli.py -OO --compress --target-dir=arky-cli-win32 --icon=ark.ico
C:\Users\Bruno\upx.exe --best arky-cli.win32\python*.dll
C:\Users\Bruno\upx.exe --best arky-cli.win32\*.pyd
