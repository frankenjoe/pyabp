import glob
import os
import warnings
import logging
from enum import Enum

from tinytag import TinyTag

import tools
from playlist import Playlist
from meta import Meta
from config import Config
from database import Database


class Scanner:


    logger = None
    database = None
    config = None


    def __init__(self, config: Config, database : Database, logger=None):

        self.config = config
        self.database = database
        self.logger = logger


    def clean(self, path: str, root: str) -> str:

        path = path[len(root):]
        if path.startswith('\\') or path.startswith('/'):
            path = path[1:]

        return path


    def scan(self) -> list:

        playlists = []
        
        if not self.database or not self.config:
            return playlists

        self.database.clean()
        tools.info('scan ' + self.config.rootDir, self.logger)

        for root,dirs,files in os.walk(os.path.join(self.config.rootDir, self.config.subDir)):                 

            playlist = self.scanDir(root)        
            if playlist:
                playlists.append(playlist) 

        return playlists


    def scanDir(self, root: str) -> Playlist:     
                
        if os.path.isdir(root):
            
            files = tools.getfiles(root, self.config.scanExtensions)

            if files:

                files.sort()

                playlist = Playlist()
                playlist.rootDir = self.config.rootDir 
                playlist.bookDir = self.clean(root, self.config.rootDir)
                playlist.files = [os.path.basename(file) for file in files]

                time = os.path.getmtime(root)    
                meta = None           

                if self.database.contains(root):    
                    meta = self.database.read(root)

                if self.config.scanAll or \
                    (self.config.scanNew and not meta) or \
                    (self.config.scanModified and meta and time != meta.modified):

                    meta = self.scanHelp(root, time, files) 

                    self.database.write(meta)
                
                if meta:
                    playlist.meta = meta
                    return playlist

        return None        


    def scanHelp(self, root: str, time: float, files: list) -> Meta: 

        tools.info('scan ' + root, self.logger) 

        meta = Meta()       
        meta.root = root 
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
            tools.error('could not read tag: ' + path, self.logger)
            
        return meta
        

if __name__ == '__main__':
    
    config = Config()
    config.read('../pyabp.init')

    database = Database()
    database.open('../pyabp.json')

    scanner = Scanner(config, database)
    playlists = scanner.scan()
    for playlist in playlists:
        playlist.print()

    database.close()
