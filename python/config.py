import os
import logging

import tools
from configparser import ConfigParser


class Config:
    

    logger = None
    startMpd = True
    confPath = ''  
    rootDir = ''  
    subDir = ''
    lastDir = ''
    exportDir = ''    
    exportSpecial = False
    isPlaying = False
    fullScreen = False
    fontSize = 16        
    scanAll = False
    scanNew = True
    scanModified = True
    scanExtensions = ['mp3','ogg','wav','flac']


    def __init__(self, logger=None):

        self.logger = logger


    def read(self, path, logger=None):

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
                self.exportSpecial = False if int(config['EXPORT']['exportSpecial']) <= 0 else True

                self.isPlaying = False if int(config['GUI']['isPlaying']) <= 0 else True            
                self.fullScreen = False if int(config['GUI']['fullScreen']) <= 0 else True
                self.fontSize = int(config['GUI']['fontSize'])

                self.scanAll = False if int(config['SCAN']['scanAll']) <= 0 else True 
                self.scanNew = False if int(config['SCAN']['scanNew']) <= 0 else True 
                self.scanModified = False if int(config['SCAN']['scanModified']) <= 0 else True     
                self.scanExtensions = config['SCAN']['scanExtensions'].split(';')        

            except:
                tools.error('could not read config file "' + path + '"', logger)

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
            'exportSpecial' : 1 if self.exportSpecial else 0, 
        }
        config['GUI'] = { 
            'isPlaying' : 1 if self.isPlaying else 0, 
            'fullScreen' : 1 if self.fullScreen else 0,
            'fontSize' : self.fontSize ,
        }        
        config['SCAN'] = { 
            'scanAll' : 1 if self.scanAll else 0, 
            'scanNew' : 1 if self.scanNew else 0,
            'scanModified' : 1 if self.scanModified else 0,
            'scanExtensions' : ';'.join(self.scanExtensions)
        }
        with open(path, 'w') as fp:
            config.write(fp)
                          

    def print(self, logger=None):        

        tools.info('startMpd=' + str(self.startMpd), logger)
        tools.info('confPath=' + self.confPath, logger)
        tools.info('rootDir=' + self.rootDir, logger)      
        tools.info('subDir=' + self.subDir, logger)
        tools.info('lastDir=' + self.lastDir, logger)
        tools.info('exportDir=' + self.exportDir, logger)
        tools.info('exportSpecial=' + str(self.exportSpecial), logger)
        tools.info('isPlaying=' + str(self.isPlaying), logger)
        tools.info('fullScreen=' + str(self.fullScreen), logger)
        tools.info('fontSize=' + str(self.fontSize), logger)
        tools.info('scanAll=' + str(self.scanAll), logger)
        tools.info('scanNew=' + str(self.scanNew), logger)
        tools.info('scanModified=' + str(self.scanModified), logger)
        tools.info('scanExtensions=' + ';'.join(self.scanExtensions), logger)


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
    config.scanAll = True
    config.scanNew = False
    config.scanModified = False
    config.write(path)

    config2 = Config()
    config2.read(path)
    config2.tools.info()

