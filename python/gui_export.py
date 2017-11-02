import sys
import psutil
import os
import shutil

from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (Qt, QTime, QEvent, QRect)
from PyQt5.QtWidgets import (QApplication, QWidget, QDesktopWidget, QWizard, QWizardPage, QComboBox, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QLayout)

import tools
from gui_library import Library
from playlist import Playlist
from config import Config
from scanner import Scanner
from gui_log import Log


CONFFILE = '../pyabp.init'


def askUser(parent: QWidget, text: str):

    reply = QMessageBox.question(parent, 'Question', text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.No:
        return False
    else:
        return True



class PageSelectAudiobook(QWizardPage):
    

    def __init__(self, config: Config, font: QFont):

        super().__init__()  

        self.setTitle('Select Audiobook')
        self.setSubTitle('Select the audiobook you want to copy (use the search field to filter the results)')
        self.setFont(font)
        self.config = config

        self.scanner = Scanner()
        playlists = self.scanner.scan(self.config)
        
        self.library = Library(playlists, font=font)
        self.library.view.clicked.connect(self.libraryClicked) 

        layout = QVBoxLayout()        
        layout.addWidget(self.library)
        self.setLayout(layout)

        
    def initializePage(self):
    
        pass


    def isComplete(self):

        playlist = self.library.getPlaylist()

        if playlist:
            self.config.playlist = playlist
            return True

        return False


    def libraryClicked(self, index):

        self.completeChanged.emit()


class PageSelectDrive(QWizardPage):

    def __init__(self, config: Config, font: QFont):

        super().__init__()  
        
        self.setTitle('Select Drive')      
        self.setSubTitle('Select the drive to which the audiobook should be copied (existing audio files will be deleted)')
        self.setFont(font)  
        self.config = config

        self.label = QLabel('')
        self.label.setFont(font)

        self.log = Log()
        self.log.console.setFont(font)

        self.comboBoxDisk = QComboBox()
        self.comboBoxDisk.setFont(font)
        self.comboBoxDisk.currentTextChanged.connect(self.comboboxChanged)
        self.comboBoxDisk.addItems(self.disks(removeableonly=True))

        layout = QVBoxLayout()        
        layout.addWidget(self.comboBoxDisk)       
        layout.addWidget(self.label)  
        layout.addWidget(self.log)  
 
        self.setLayout(layout)


    def comboboxChanged(self):

        root = self.comboBoxDisk.currentText()
    
        if os.path.exists(root):
            self.files = tools.getfiles(root, self.config.scanExtensions)
            if len(self.files) > 0:
                self.label.setText ('<font color="red">WARNING: ' + str(len(self.files)) + ' files will be deleted</font>')   
            else:
                self.label.setText ('No files will be deleted')   


    def initializePage(self):

        pass 


    def isComplete(self):

        root = self.comboBoxDisk.currentText()
    
        if root and os.path.exists(root):
            self.config.exportDir = root
            return True

        return False


    def validatePage(self):

        return self.clear()
        
        
    def clear(self):

        root = self.config.exportDir
    
        try:

            for file in self.files:
                self.log.print('delete ' + os.path.join(root, file))        
                os.remove(os.path.join(root, file))     

        except Exception as ex:

            self.log.print(str(ex))
            return False

        return True


    def disks(self, removeableonly=False):
        
        partitions = []
        
        if self.config.exportDir and os.path.exists(self.config.exportDir):
            partitions.append(self.config.exportDir)

        for partition in psutil.disk_partitions():     
            tokens = partition.opts.split(',')            
            if tools.islinux():
                if not removeableonly or 'flush' in tokens:
                    partitions.append(partition.mountpoint)
            else:
                if not removeableonly or 'removable' in tokens:
                    partitions.append(partition.mountpoint)

        return partitions


class PageCopy(QWizardPage):


    def __init__(self, config: Config, font: QFont, firstOnly: bool = False):

        super().__init__()  

        self.setTitle('Copy file(s)')
        self.setSubTitle('Click "Next" to copy the first file of the audiobook.' if firstOnly else 'Click "Next" to copy all files of the audiobook.')
        self.setFont(font)
        self.firstOnly = firstOnly
        self.config = config

        font = QFont()
        font.setPixelSize(self.config.fontSize)

        self.log = Log()
        self.log.console.setFont(font)

        layout = QVBoxLayout()
        layout.addWidget(self.log)
        self.setLayout(layout)


    def initializePage(self):
    
        pass


    def isComplete(self):

        return True


    def validatePage(self):

        return self.copy()


    def copy(self):

        try:

            root = self.config.exportDir
            if os.path.exists(root):
                playlist = self.config.playlist
                if playlist:
                    playlist.export(root, 1 if self.firstOnly else 5, log = self.log)

        except Exception as ex:

                self.log.print(ex)
                return False

        return True


class PageFinal(QWizardPage):


    def __init__(self, config: Config, font: QFont, firstOnly: bool = False):

        super().__init__()  

        self.setTitle('Finished')
        self.setSubTitle('The audiobook was successfully copied to the drive. Enjoy listening.')
        self.setFont(font)


class Export(QWizard):


    def __init__(self, parent = None):

        super().__init__()  

        rect = QDesktopWidget().screenGeometry(-1)
        width = rect.width() * 0.75;
        height = rect.height() * 0.75;        
        left = (rect.width() - width) / 2
        top = (rect.height() - height) / 2
        self.setGeometry(left, top, width, height) 

        self.config = self.readConfig()

        font = QFont()
        font.setPixelSize(self.config.fontSize)

        self.parent = parent
        self.setWindowTitle("Export Playlist")
        #self.setFont(font)

        self.addPage(PageSelectAudiobook(self.config, font))
        self.addPage(PageSelectDrive(self.config, font))
        if self.config.exportSpecial:
            self.addPage(PageCopy(self.config, font, firstOnly = True))        
        self.addPage(PageCopy(self.config, font))
        self.addPage(PageFinal(self.config, font))

        self.show()    


    def readConfig(self):
        
        config = Config()
        config.playlist = None

        if os.path.exists(CONFFILE):            
            config.read(CONFFILE)   

        return config
        

    #def writeConfig(self):
    #               
    #    self.config.write(CONFFILE)


if __name__ == '__main__':    

    app = QApplication(sys.argv)
    ex = Export()
    sys.exit(app.exec_())    
   
