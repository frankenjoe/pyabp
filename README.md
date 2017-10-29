# pyabp

Python Audiobook Player

# Dependencies

* pip3 install pyqt5 (linux: sudo apt-get install python3-pyqt5)

* pip3 install tinytag

* pip3 install python-mpd2

* pip3 install psutil

# Windows

* copy https://www.musicpd.org/download/win32/0.20.10/mpd.exe to .\mpd

* edit .\mpd\mpd.conf and set 'music_directory'

* pyabp.cmd

# Linux

* install [https://www.musicpd.org/](mpd)

- sudo apt-get install mpd

- systemctl disable mpd

- mkdir ~/.config/mpd

- gunzip -c /usr/share/doc/mpd/mpdconf.example.gz > ~/.config/mpd/mpd.conf 

- gedit ~/.config/mpd/mpd.conf, uncomment the following entries and set to ~/.config/mpd/<entry>

music_directory
playlist_directory
db_file
log_file
pid_file
state_file 

- uncomment the desired output (e.g. ALSA output)

- create '~/.config/autostart/mpd.desktop'

[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=Music Player Daemon
Comment=Server for playing audio files
Exec=mpd
StartupNotify=true
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true

- mpd (or restart system)

* ./pyabp.sh


