import os
from configparser import ConfigParser


class Config:
    

    exportPath = ''
    isPlaying = False
    currentPath = ''
    fullScreen = False
    fontSize = 16        


    def read(self, path):

        config = ConfigParser()
        if os.path.exists(path):
            config.read(path)
            try:
                self.currentPath = config['DEFAULT']['currentPath']
                self.exportPath = config['DEFAULT']['exportPath']            
                self.isPlaying = False if int(config['DEFAULT']['isPlaying']) <= 0 else True            
                self.fullScreen = False if int(config['DEFAULT']['fullScreen']) <= 0 else True
                self.fontSize = int(config['DEFAULT']['fontSize'])
            except:
                print('could not read config file "' + path + '"')

    def write(self, path):

        config = ConfigParser()                    
        config['DEFAULT'] = { 'currentPath' : self.currentPath, 
            'isPlaying' : 1 if self.isPlaying else 0, 
            'exportPath' : self.exportPath, 
            'fullScreen' : 1 if self.fullScreen else 0,
            'fontSize' : self.fontSize }
        with open(path, 'w') as fp:
            config.write(fp)
                          

    def print(self):        

        print('exportPath=' + self.exportPath)
        print('isPlaying=' + str(self.isPlaying))
        print('currentPath=' + self.currentPath)
        print('fullScreen=' + str(self.fullScreen))
        print('fontSize=' + str(self.fontSize))


if __name__ == '__main__':

    config = Config()
    config.exportPath = '.'
    config.isPlaying = True
    config.currentPath = '.'
    config.fullScreen = True
    config.fontSize = 12
    config.write('config.init')

    config2 = Config()
    config2.read('config.init')
    config2.print()

