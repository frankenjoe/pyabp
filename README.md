# pyabp

Python Audiobook Player

# Dependencies

pip3 install pyqt5 (or: sudo apt-get install python3-pyqt5)

pip3 install tinytag

pip3 install python-mpd2

pip3 install psutil

# Windows

copy https://www.musicpd.org/download/win32/0.20.10/mpd.exe to .\mpd

edit .\mpd\mpd.conf and set 'music_directory'

pyabp.cmd

# Linux

copy /etc/mpd.conf to ~/.config/mpd/mpd.conf and set 'music_directory'

sudo systemctl start mpd

./pyabp.sh


