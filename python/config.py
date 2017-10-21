import os

import tools
from configparser import ConfigParser


class Config:
    

    startMpd = True
    confPath = ''  
    rootDir = ''  
    subDir = ''
    lastDir = ''
    exportDir = ''    
    isPlaying = False
    fullScreen = False
    fontSize = 16        


    def read(self, path):

        config = ConfigParser()
        if os.path.exists(path):
            config.read(path)
            try:

                self.startMpd = False if int(config['MPD']['startMpd']) <= 0 else True         
                self.confPath = config['MPD']['confPath']  
                self.rootDir = tools.getroot(self.confPath)          
                self.subDir = config['MPD']['subDir']            
                self.lastDir = config['MPD']['lastDir']

                self.exportDir = config['EXPORT']['exportDir']            

                self.isPlaying = False if int(config['GUI']['isPlaying']) <= 0 else True            
                self.fullScreen = False if int(config['GUI']['fullScreen']) <= 0 else True
                self.fontSize = int(config['GUI']['fontSize'])

            except:
                print('could not read config file "' + path + '"')

    def write(self, path):

        config = ConfigParser()                    
        config['MPD'] = { 
            'startMpd' : 1 if self.startMpd else 0, 
            'confPath' : self.confPath,
            'subDir' : self.subDir, 
            'lastDir' : self.lastDir, 
        }
        config['EXPORT'] = {
            'exportDir' : self.exportDir, 
        }
        config['GUI'] = { 
            'isPlaying' : 1 if self.isPlaying else 0, 
            'fullScreen' : 1 if self.fullScreen else 0,
            'fontSize' : self.fontSize ,
        }
        with open(path, 'w') as fp:
            config.write(fp)
                          

    def print(self):        

        print('startMpd =', self.startMpd)
        print('confPath =', self.confPath)
        print('rootDir =', self.rootDir)      
        print('subDir =', self.subDir)
        print('lastDir =', self.lastDir)
        print('exportDir =', self.exportDir)
        print('isPlaying =', self.isPlaying)
        print('fullScreen =', self.fullScreen)
        print('fontSize =', self.fontSize)


if __name__ == '__main__':

    path = 'config.init'

    tools.remfile(path)

    config = Config()
    config.startMpd = 1
    config.confPath = '../mpd/mpd.conf'
    config.subDir = 'sub/dir'
    config.lastDir = 'last/dir'
    config.exportDir = '/export'
    config.isPlaying = True
    config.fullScreen = True
    config.fontSize = 12
    config.write(path)

    config2 = Config()
    config2.read(path)
    config2.print()

