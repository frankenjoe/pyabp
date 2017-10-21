import glob
import os
import warnings

from tinytag import TinyTag

import tools
from playlist import Playlist
from meta import Meta


EXTENSIONS = ['mp3', 'ogg']


class Scanner:


    def clean(self, path, root):
        path = path[len(root):]
        if path.startswith('\\') or path.startswith('/'):
            path = path[1:]
        return path


    def scan(self, mpddir, subdir, force=False):
        
        playlists = []

        for root,dirs,files in os.walk(os.path.join(mpddir, subdir)):                
            playlist = self.scandir(root, mpddir, force)        
            if playlist:
                playlists.append(playlist) 

        return playlists


    def scandir(self, root, mpddir, force):     
                
        if os.path.isdir(root):
            
            files = []
            for ext in EXTENSIONS:
                files.extend(glob.glob(os.path.join(root, '*.' + ext)))

            if files:

                files.sort()

                playlist = Playlist()
                playlist.rootDir = mpddir 
                playlist.bookDir = self.clean(root, mpddir)
                playlist.files = [os.path.basename(file) for file in files]

                metapath = os.path.join(root, 'meta.json')
                if os.path.exists(metapath) and not force:
                    #print('load ' + root)
                    playlist.meta = Meta()
                    playlist.meta.read(metapath)                    
                else:                    
                    print('scan ' + root)           
                    meta = Meta()        
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

                    meta.write(metapath)
                    playlist.meta = meta

                    playlist.print()

                return playlist

        return None        


if __name__ == '__main__':
    
    root = tools.getroot('..\\mpd\\mpd.conf')
    sub = 'Audiobooks'
    force = True
                      
    scanner = Scanner()
    playlists = scanner.scan(root, sub, force=force)
    for playlist in playlists:
        playlist.print()
