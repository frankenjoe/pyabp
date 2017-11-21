@echo off

cd python
pyinstaller --onefile --windowed --icon=pics\player.ico --noconsole pyabp.py
move dist\pyabp.exe ..\bin\win64\pyabp.exe