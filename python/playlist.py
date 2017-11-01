import glob
import os
from tinytag import TinyTag
import warnings
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


    def export(self, root, count = 0, log = None):

        if count == 0:
            count = len(self.files)

        for file in self.files:
            src = os.path.join(self.rootDir, self.bookDir, file)            
            dst = os.path.join(root, file)
            if log:
                log.print('copy ' + src + ' > ' + dst)          
            print('copy ' + src + ' > ' + dst)
            tools.copyfile(src, dst)
            count = count - 1

            if count == 0:
                break


    def print(self):

        print('-'*30)
        print(self.bookDir)
        print('-'*30)                
        if self.meta:
            self.meta.print()     
        print('-'*30)              
        print(self.files[0])
        print('...')
        print(self.files[-1])
        print('-'*30)        


if __name__ == '__main__':
    
    playlist = Playlist()
    playlist.meta = Meta()
    playlist.root = tools.randstr()
    for i in range(10):
        playlist.files.append(tools.randstr())
    playlist.print()
