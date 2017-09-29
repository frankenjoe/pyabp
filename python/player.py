import os
from mpd import MPDClient
import playlist as pl
import time
import config

class Player:

    root = ''
    playlist = None
    client = None
    isPlay = False


    def __init__(self, confpath, host='localhost', port=6600):

        try:
            client = MPDClient()
            client.connect(host, port)
            print(client.mpd_version)
            self.client = client    
            self.root = config.read(confpath, 'music_directory')        
        except:
            warnings.warn('could not connect mpd: ' + confpath)
        

    def update(self):
        
        if not self.client:
            return

        self.client.rescan()


    def load(self, playlist):
        
        if not self.client:
            return

        self.stop()

        self.playlist = playlist
        self.client.clear()        

        for file in playlist.files:
            path = file.replace('\\', '/')
            if self.root and path.startswith(self.root):
                path = path[len(self.root):]
                if path.startswith('/'):
                    path = path[1:]
            self.client.add(path)


    def toggle(self):

        if not self.client:
            return

        if self.isPlay:
            self.stop()
        else:
            self.play()	


    def play(self):

        if not self.client or self.isPlay:
            return

        track = min(self.playlist.meta.track, self.playlist.meta.ntracks)            
        position = self.playlist.meta.position 
        print('play ' + str(track) + '>' + str(position))
        self.client.play()
        self.client.seek(track, position)
        self.isPlay = True


    def stop(self):     

        if not self.client or not self.isPlay:
            return     
   
        status = self.client.status()		    		    		
        self.client.stop()
        self.isPlay = False

        track = status['song']
        position = status['elapsed']
        volume = status['volume']            
            
        print('stop ' + str(track) + '>' + str(position))

        self.playlist.meta.position = float(position)
        self.playlist.meta.track = int(track)
        self.playlist.meta.write()


if __name__ == '__main__':
    
    path = 'F:\\Audiobooks\\Andere\\Edgar Allan Poe\\Das Fass Amontillado'
    confpath = '..\\mpd\\mpd.conf'

    playlist = pl.Playlist()
    playlist.parse(path)
    playlist.print()
    
    player = Player(confpath)
    player.load(playlist)    
    player.play()    
    time.sleep(3)
    player.toggle()
    time.sleep(1)
    player.toggle()
    time.sleep(3)
    player.stop()
