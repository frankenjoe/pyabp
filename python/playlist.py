import glob
import os
from tinytag import TinyTag
import warnings
import tools
from meta import Meta


class Playlist:


    root = None        
    ext = '.mp3'
    meta = None    
    files = []

    def write(self, path):

        if len(files) > 0:
            with open(path, 'w') as fp:		            
                for file in self.files:
                    name, ext = os.path.splitext(file)                
                    path = os.path.join(self.root, file)                
                    fp.write(path + '\n')


    def export(self, root, count = 1):

        for file in self.files:
            src = os.path.join(self.root, file)
            name, ext = os.path.splitext(src)
            dst = os.path.join(root, 'pyabp' + str(count).zfill(4)) + ext
            print('copy ' + src + ' > ' + dst)
            tools.copyfile(src, dst)
            count = count + 1


    def print(self, n_files=5):

        print('-'*30)
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
    
    playlist = Playlist()
    playlist.meta = Meta()
    playlist.root = tools.randstr()
    for i in range(10):
        playlist.files.append(tools.randstr())
    playlist.print()
