import os
import time
import warnings

from PersistentMPDClient import PersistentMPDClient
from tinytag import TinyTag

import tools
from scanner import Scanner


class Player:


    host = '127.0.0.1'
    port = 6600
    playlist = None
    client = None
    isPlay = False


    def connect(self, host='127.0.0.1', port=6600):

        self.host = host
        self.port = port

        return self.init()
           
            
    def init(self):

        try:                      

            self.client = PersistentMPDClient(host=self.host, port=self.port)
            return True 

        except Exception as ex:
            warnings.warn(ex)
            
        return False        


    def close(self):
        
        if not self.client:
            return

        self.stop()

        try:        
            self.client.close()
        except Exception as ex:
            print(ex)            


    def update(self):
        
        if not self.client:
            return

        try:
            self.client.rescan()
        except Exception as ex:
            print(ex)


    def load(self, playlist):
        
        if not self.client:
            return

        self.stop()

        try:

            self.playlist = playlist
            self.client.clear()        

            for file in playlist.files:
                path = os.path.join(playlist.bookDir, file).replace('\\', '/')                 
                self.client.add(path)

            self.volume(playlist.meta.volume)

        except Exception as ex:
            print(ex)


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


    def move(self, position):

        if not self.client or not self.playlist:
            return  

        if not self.isPlay:

            self.playlist.meta.position = position

        else:

            try:
                self.client.seekcur(position)
            except Exception as ex:
                print(ex) 


    def stop(self):     

        if not self.client or not self.playlist:
            return     

        if not self.isPlay:            
            self.playlist.meta.write()

        else:

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


    def next(self):
        
        if not self.client or not self.playlist:
            return  

        if not self.isPlay:
            length = len(self.playlist.files)
            if self.playlist.meta.track < length - 1:
                self.playlist.meta.track = self.playlist.meta.track + 1
                self.playlist.meta.position = 0
            
        else:

            try:          
                (track, length, position, duration, path) = self.status()
                if track < length - 1:
                    self.client.next()
            except Exception as ex:
                print(ex)


    def previous(self):
        
        if not self.client or not self.playlist:
            return  

        if not self.isPlay:
            length = len(self.playlist.files)
            if self.playlist.meta.track > 0:
                self.playlist.meta.track = self.playlist.meta.track - 1
                self.playlist.meta.position = 0

        else:

            try:
                (track, length, position, duration, path) = self.status()
                if track > 0:                
                    self.client.previous()
            except Exception as ex:
                print(ex)


    def restart(self):
        
        if not self.client or not self.playlist:
            return  

        if not self.isPlay:
            self.playlist.meta.track = 0
            self.playlist.meta.position = 0

        else:

            try:
                self.client.seek(0,0.0)
            except Exception as ex:
                print(ex)             


    def volume(self, value):    
        
        if not self.client or not self.playlist:
            return  

        value = max(0,min(100,value))
        self.playlist.meta.volume = value            

        try:
            self.client.setvol(value)
        except Exception as ex:
            print(ex)


    def volumeUp(self):

        self.volume(self.playlist.meta.volume + 5)


    def volumeDown(self):

        self.volume(self.playlist.meta.volume - 5)


    def status(self):
        
        if not self.client or not self.playlist:
            return (-1,0,0,0,'')  
            
        track = -1
        length = 0
        position = 0
        duration = 0        
        path = ''

        if not self.isPlay:

            track = self.playlist.meta.track
            path = os.path.join(self.playlist.rootDir, self.playlist.bookDir, self.playlist.files[track])
            length = len(self.playlist.files)
            position = self.playlist.meta.position           
               
            try:
                tag = TinyTag.get(path)
                duration = tag.duration
            except:
                duration = 0.0
               
        else:

            try:
                   
                status = self.client.status()

                state = status['state']
                if state == 'stop':
                    self.isPlay = False
                    self.restart()
                    self.play()
                    return self.status()

                track = int(status['song'])
                path = self.playlist.files[track]
                length = int(status['playlistlength'])
                position = float(status['elapsed'])
                duration = float(status['duration'])

            except Exception as ex:
                print(ex)    

        return (track,length,position,duration,path)


if __name__ == '__main__':
    
    root = tools.getroot('..\\mpd\\mpd.conf')
    sub = 'Audiobooks'

    scanner = Scanner()
    playlists = scanner.scan(root, sub)

    if len(playlists) > 0:
        
        playlist = playlists[0]
        playlist.print()
    
        player = Player()

        if player.connect():
            player.load(playlist)    
            player.play()    
            time.sleep(3)
            player.toggle()
            time.sleep(1)
            player.toggle()
            time.sleep(3)
            player.close()
