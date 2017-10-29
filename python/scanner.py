import glob
import os
import warnings
from enum import Enum

from tinytag import TinyTag

import tools
from playlist import Playlist
from meta import Meta
from config import Config


EXTENSIONS = ['mp3', 'ogg']


class Scanner:


    def clean(self, path: str, root: str) -> str:

        path = path[len(root):]
        if path.startswith('\\') or path.startswith('/'):
            path = path[1:]

        return path


    def scan(self, config: Config) -> list:
        
        playlists = []

        for root,dirs,files in os.walk(os.path.join(config.rootDir, config.subDir)):                 

            playlist = self.scanDir(root, config)        
            if playlist:
                playlists.append(playlist) 

        return playlists


    def scanDir(self, root: str, config: Config) -> Playlist:     
                
        if os.path.isdir(root):
            
            files = []
            for ext in EXTENSIONS:
                files.extend(glob.glob(os.path.join(root, '*.' + ext)))

            if files:

                files.sort()

                playlist = Playlist()
                playlist.rootDir = config.rootDir 
                playlist.bookDir = self.clean(root, config.rootDir)
                playlist.files = [os.path.basename(file) for file in files]

                metapath = os.path.join(root, 'meta.json')
                time = os.path.getmtime(root)    

                meta = None           
                if os.path.exists(metapath):
                    meta = Meta()
                    meta.read(metapath)       

                if config.scanAll or \
                    (config.scanNew and not meta) or \
                    (config.scanModified and meta and time - meta.modified > 60):

                    meta = self.scanHelp(root, time, files, config) 
                    meta.write(metapath) 
                
                if meta:
                    playlist.meta = meta
                    return playlist

        return None        


    def scanHelp(self, root: str, time: float, files: list, config: Config) -> Meta: 

        print('scan ' + root) 

        meta = Meta()        
        meta.modified = time
        path = os.path.join(root, files[0])         

        try:
            tag = TinyTag.get(path)
            meta.ntracks = len(files)
            if tag.artist:
                meta.artist = tag.artist
            if tag.album:
                meta.album = tag.album
            duration = 0.0
            for file in files:   
                path = os.path.join(root, file)
                tag = TinyTag.get(path)
                if tag.duration:
                    duration = duration + tag.duration
            meta.duration = duration
        except:
            warnings.warn('could not read mp3 tag: ' + path)
            
        return meta
        

if __name__ == '__main__':
    
    config = Config()
    config.read('../pyabp.init')

    scanner = Scanner()
    playlists = scanner.scan(config)
    for playlist in playlists:
        playlist.print()
