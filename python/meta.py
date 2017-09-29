import os
import json
import pprint
import random
import datetime
import tools


class Meta:
    

    path = None
    artist = ''
    album = ''
    track = 0
    ntracks = 0
    position = 0
    duration = 0.0
    info = ''


    def positionstr(self):
        return str(datetime.timedelta(seconds=int(self.position)))


    def durationstr(self):
        return str(datetime.timedelta(seconds=int(self.duration)))
       

    def read(self, path = None):    
        if path != None:
            self.path = path
        if self.path != None and os.path.exists(self.path):
            with open(self.path, 'r') as fp:    
                data = json.load(fp)
                self.album = data['album']
                self.artist = data['artist']
                self.ntracks = data['ntracks']
                self.duration = data['duration']
                self.track = data['track']
                self.position = data['position']
                self.info = data['info']


    def write(self, path = None):
        if path != None:
            self.path = path
        if self.path != None:
            data = {}
            data['album'] = self.album
            data['artist'] = self.artist            
            data['ntracks'] = self.ntracks
            data['duration'] = self.duration
            data['track'] = self.track
            data['position'] = self.position
            data['info'] = self.info
            with open(self.path, 'w') as fp:    
                json.dump(data, fp)
                          

    def print(self):        
        print('artist=' + self.artist)
        print('album=' + self.album)
        print('track=' + str(self.track+1) + '/' + str(self.ntracks))        
        print('position=' + self.positionstr())
        print('total=' + self.durationstr())
        print('info=' + self.info)


if __name__ == '__main__':

    meta = Meta()
    meta.read('meta.json')
    meta.print()
    meta.album = tools.randstr()
    meta.artist = tools.randstr()
    meta.ntracks = 100
    meta.track = random.randint(0, meta.ntracks-1)
    meta.position = round(random.uniform(0.0,60.0), 1)
    meta.info =  tools.randstr()
    meta.print()
    meta.write()
