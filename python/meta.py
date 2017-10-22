import os
import json
import pprint
import random
import tools


class Meta:
    

    path = None
    artist = ''
    album = ''
    track = 0
    ntracks = 0
    position = 0
    duration = 0.0
    volume = 50
    modified = None


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
            self.volume = data['volume']
            self.modified = data['modified']


    def write(self, path = None):

        if path != None:
            self.path = path

        if self.path != None:

            data = {}
            data['artist'] = self.artist  
            data['album'] = self.album          
            data['ntracks'] = self.ntracks
            data['duration'] = self.duration
            data['track'] = self.track
            data['position'] = self.position
            data['volume'] = self.volume
            data['modified'] = self.modified

            with open(self.path, 'w') as fp:    
                json.dump(data, fp)
                          

    def print(self):        
        print('artist =', self.artist)
        print('album =', self.album)
        print('track =', self.track+1, '/', self.ntracks)
        print('position =', tools.friendlytime(self.position))
        print('total =', tools.friendlytime(self.duration))
        print('volume =', self.volume)
        print('modified=', self.modified)


if __name__ == '__main__':

    meta = Meta()
    meta.album = tools.randstr()
    meta.artist = tools.randstr()
    meta.ntracks = 100
    meta.track = random.randint(0, meta.ntracks-1)
    meta.position = round(random.uniform(0.0,60.0), 1)
    meta.volume = random.randint(0, 100)
    meta.modified = 0
    meta.write('meta.json')
    
    meta2 = Meta()
    meta2.read('meta.json')
    meta2.print()
    
