import os
import time
import warnings

from mpd import MPDClient

import tools
from scanner import Scanner


class Player:

    root = ''
    playlist = None
    client = None
    isPlay = False


    def connect(self, root, host='127.0.0.1', port=6600):

        try:
            client = MPDClient()
            client.connect(host, port)
            print(client.mpd_version)
            self.client = client    
            self.root = root        

            return True

        except:
            warnings.warn('could not connect mpd')
    
        return False
        

    def close(self):
        
        if not self.client:
            return

        self.stop()
        self.client.close()


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

        for path in playlist.files:
            if self.root and path.startswith(self.root):
                path = path[len(self.root):]
                if path.startswith('\\'):
                    path = path[1:]
                path = path.replace('\\', '/')
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
    
    root = tools.getroot()

    scanner = Scanner()
    playlists = scanner.scan(root)

    if len(playlists) > 0:
        
        playlist = playlists[0]
        playlist.print()
    
        player = Player()

        if player.connect(root):
            player.load(playlist)    
            player.play()    
            time.sleep(3)
            player.toggle()
            time.sleep(1)
            player.toggle()
            time.sleep(3)
            player.close()
