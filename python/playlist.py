import meta as m
import glob
import os
from tinytag import TinyTag
import warnings
import config


class Playlist:


    root = None        
    ext = '.mp3'
    meta = None    
    files = []


    def fullname(self):
        if self.root != None:
            return self.root.replace('\\', '.') + 'm3u'
        else:
            return None


    def parse(self, root = None, ext = '.mp3', force = False):     
                
        if root != None:
            self.root = root

        if self.root != None and os.path.isdir(self.root):
            files = glob.glob(os.path.join(self.root, '*' + self.ext)) 
            if len(files) > 0:   
                self.files = files
                self.ext = ext
                metapath = os.path.join(self.root, 'meta.json')
                if os.path.exists(metapath) and not force:
                    self.meta = m.Meta()
                    self.meta.read(metapath)
                else:                               
                    meta = m.Meta()        
                    mp3path = os.path.join(self.root, files[0])         
                    try:
                        tag = TinyTag.get(mp3path)
                        meta.ntracks = len(self.files)
                        if tag.artist:
                            meta.artist = tag.artist
                        if tag.album:
                            meta.album = tag.album
                        duration = 0.0
                        for file in files:   
                            mp3path = os.path.join(self.root, file)
                            tag = TinyTag.get(mp3path)
                            if tag.duration:
                                duration = duration + tag.duration
                        meta.duration = duration
                    except:
                        warnings.warn('could not read mp3 tag: ' + mp3path)
                    meta.write(metapath)
                    self.meta = meta
                return True

        return False        


    def write(self, path):

        if len(files) > 0:
            with open(path, 'w') as fp:		            
                for file in self.files:
                    name, ext = os.path.splitext(file)                
                    path = os.path.join(self.root, file)                
                    fp.write(path + '\n')


    def print(self, n_files=5):

        print('-'*60)
        print(self.root);
        print('-'*30)                
        if self.meta:
            self.meta.print()                
        print('-'*30)         
        for i in range(0,min(n_files,len(self.files))):
            print(os.path.basename(self.files[i]))
        if len(self.files) > n_files:
            print('...')
            print(os.path.basename(self.files[-1]))
        print('-'*30)        


if __name__ == '__main__':
    
    confpath = '..\\mpd\\mpd.conf'
    root = config.read(confpath, 'music_directory')
    force = True
           
    for root,dirs,files in os.walk(root):                
        playlist = Playlist()        
        if playlist.parse(root, force=force):
            playlist.print()            
    
