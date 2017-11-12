import glob
import os
from tinytag import TinyTag
import warnings
import logging

import tools
from meta import Meta


class Playlist:


    rootDir = None     
    bookDir = None   
    files = []
    meta = None    


    def write(self, path):

        if len(files) > 0:
            with open(path, 'w') as fp:		            
                for file in self.files:
                    name, ext = os.path.splitext(file)                
                    path = os.path.join(self.rootDir, self.bookDir, file)                
                    fp.write(path + '\n')


    def print(self, logger=None):

        tools.info('-'*30, logger)
        tools.info(self.bookDir, logger)
        tools.info('-'*30, logger)                
        if self.meta:
            self.meta.print(logger)     
        tools.info('-'*30, logger)              
        tools.info(self.files[0], logger)
        tools.info('...', logger)
        tools.info(self.files[-1], logger)
        tools.info('-'*30, logger)        


if __name__ == '__main__':
    
    playlist = Playlist()
    playlist.meta = Meta()
    playlist.root = tools.randstr()
    for i in range(10):
        playlist.files.append(tools.randstr())
    playlist.print()
