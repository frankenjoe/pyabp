import glob
import os
from tinytag import TinyTag
import warnings
import tools
from playlist import Playlist
from meta import Meta


class Scanner:

    def scan(self, root, ext='.mp3', force=False):
        
        playlists = []

        for root,dirs,files in os.walk(root):                
            playlist = self.scandir(root, force=force)        
            if playlist:
                playlists.append(playlist) 

        return playlists


    def scandir(self, root, ext='.mp3', force=False):     
                
        if os.path.isdir(root):
            files = glob.glob(os.path.join(root, '*' + ext)) 
            if len(files) > 0:
                playlist = Playlist()
                playlist.root = root
                playlist.files = files
                playlist.ext = ext

                metapath = os.path.join(root, 'meta.json')
                if os.path.exists(metapath) and not force:
                    playlist.meta = Meta()
                    playlist.meta.read(metapath)
                else:                               
                    meta = Meta()        
                    mp3path = os.path.join(root, files[0])         
                    try:
                        tag = TinyTag.get(mp3path)
                        meta.ntracks = len(files)
                        if tag.artist:
                            meta.artist = tag.artist
                        if tag.album:
                            meta.album = tag.album
                        duration = 0.0
                        for file in files:   
                            mp3path = os.path.join(root, file)
                            tag = TinyTag.get(mp3path)
                            if tag.duration:
                                duration = duration + tag.duration
                        meta.duration = duration
                    except:
                        warnings.warn('could not read mp3 tag: ' + mp3path)

                    meta.write(metapath)
                    playlist.meta = meta

                return playlist

        return None        


if __name__ == '__main__':
    
    confpath = '..\\mpd\\mpd.conf'
    root = tools.readconf(confpath, 'music_directory')
    force = True
                      
    scanner = Scanner()
    playlists = scanner.scan(root, force=force)
    for playlist in playlists:
        playlist.print()
