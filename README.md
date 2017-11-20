# pyabp

A multi-platform AudioBook Player written in Python using [Music Player Daemon](https://www.musicpd.org/) and [PyQt5](https://pypi.python.org/pypi/PyQt5)

# Features

* Playback from last position
* Keeps list of audiobooks
* Automatically scans for new items
* Remembers playback location and volume for each title
* Runs on Windows and Linux

![player standalone](pics/pyabp1.png?raw=true "Player standalone")

![player with library](pics/pyabp2.png?raw=true "Player with library")

# Dependencies

# Windows

* edit .\bin\win64\mpd.conf and set 'music_directory'

* run .\bin\win64\pyabt.exe

# Linux

* sudo apt-get install python3-pyqt5

* pip3 install tinytag

* pip3 install python-mpd2

* pip3 install psutil

* pip3 install tinydb (>= 3.7)

* install [https://www.musicpd.org/](mpd)

	* sudo apt-get install mpd

	* systemctl disable mpd

	* mkdir ~/.config/mpd

	* gunzip -c /usr/share/doc/mpd/mpdconf.example.gz > ~/.config/mpd/mpd.conf 

	* gedit ~/.config/mpd/mpd.conf, uncomment the following entries and set to ~/.config/mpd/<entry>

	```
	music_directory
	playlist_directory
	db_file
	log_file
	pid_file
	state_file 
	```

	* uncomment the desired output (e.g. ALSA output)

	* create '~/.config/autostart/mpd.desktop'

	```
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
	```

	* mpd (or restart system)

* ./pyabp.sh

# Credits

Icon by Martz90
http://www.iconarchive.com/show/circle-icons-by-martz90/books-icon.html
