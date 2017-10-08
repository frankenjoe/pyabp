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

        self.root = root
        return self.init(host, port)       
        

    def init(self, host='127.0.0.1', port=6600):

        try:            
            self.client = MPDClient()
            self.client.connect(host, port)            
            return True

        except:
            warnings.warn('could not connect mpd')

        return False


    def close(self):
        
        if not self.client:
            return

        self.stop()

        try:        
            self.client.close()
        except Exception as ex:
            print(ex)            
            if self.init():
                self.close()


    def update(self):
        
        if not self.client:
            return

        try:
            self.client.rescan()
        except Exception as ex:
            print(ex)
            if self.init():
                self.update()


    def load(self, playlist):
        
        if not self.client:
            return

        self.stop()

        try:

            self.playlist = playlist
            self.client.clear()        

            for path in playlist.files:
                if self.root and path.startswith(self.root):
                    path = path[len(self.root):]
                    if path.startswith('\\'):
                        path = path[1:]
                    path = path.replace('\\', '/')
                    self.client.add(path)

            self.volume(playlist.meta.volume)

        except Exception as ex:
            print(ex)
            if self.init():
                self.load(playlist)


    def toggle(self):

        if self.isPlay:
            self.stop()
        else:
            self.play()	


    def play(self):

        if not self.client or not self.playlist or self.isPlay:
            return        

        try:

            track = min(self.playlist.meta.track, self.playlist.meta.ntracks)            
            position = self.playlist.meta.position 
            print('play ' + str(track) + '>' + str(position))

            self.client.play()
            self.client.seek(track, position)
            self.isPlay = True

        except Exception as ex:
            print(ex)
            if self.init():
                return self.play()


    def stop(self):     

        if not self.client or not self.playlist or not self.isPlay:
            return     

        try:    		    		
   
            status = self.client.status()		

            self.client.stop()
            self.isPlay = False
        
            track = status['song']
            position = status['elapsed']
            volume = status['volume']            
            
            print('stop ' + str(track) + '>' + str(position))

            self.playlist.meta.position = float(position)
            self.playlist.meta.track = int(track)
            self.playlist.meta.volume = int(volume)
            self.playlist.meta.write()

        except Exception as ex:
            print(ex)
            if self.init():
                return self.stop()


    def next(self):
        
        if not self.client or not self.playlist:
            return  

        try:          
            (track, length, position, duration, path) = self.status()
            if track < length - 1:
                self.client.next()
        except Exception as ex:
            print(ex)
            if self.init():
                return self.next()


    def previous(self):
        
        if not self.client or not self.playlist:
            return  

        try:
            (track, length, position, duration, path) = self.status()
            if track > 0:                
                self.client.previous()
        except Exception as ex:
            print(ex)
            if self.init():
                return self.previous()


    def restart(self):
        
        if not self.client or not self.playlist:
            return  

        try:
            self.client.seek(0,0.0)
        except Exception as ex:
            print(ex)
            if self.init():
                return self.restart()


    def volume(self, value):
        
        if not self.client or not self.playlist:
            return  

        try:
            value = max(0,min(100,value))
            self.client.setvol(value)
        except Exception as ex:
            print(ex)
            if self.init():
                return self.volume(value)


    def status(self):
        
        if not self.client or not self.playlist or not self.isPlay:
            return (-1,0,0,0,'')  

        try:    		    		
   
            status = self.client.status()	            
            track = int(status['song'])
            path = self.playlist.files[track]
            length = int(status['playlistlength'])
            position = float(status['elapsed'])
            duration = float(status['duration'])

            return (track,length,position,duration,path)

        except Exception as ex:
            print(ex)
            if self.init():
                return self.status()        


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
