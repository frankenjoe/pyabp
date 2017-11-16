import sys
import psutil
import os
import shutil
import logging

from PyQt5.QtGui import (QIcon, QFont, QPixmap)
from PyQt5.QtCore import (Qt, QTime, QEvent, QRect)
from PyQt5.QtWidgets import (QApplication, QWidget, QDesktopWidget, QWizard, QWizardPage, QProgressBar, QComboBox, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QLayout, QMessageBox, QSizePolicy)

import tools
from gui_library import Library
from playlist import Playlist
from config import Config
from scanner import Scanner
from gui_log import Log
from database import Database


LOGFILE = '../pyabpex.log'
CONFFILE = '../pyabp.init'
DBFILE = '../pyabp.json'
TITLE = 'Kopiere Audiobuch'
ICONFILE = '../pics/player.ico'


def askUser(parent: QWidget, text: str):

    reply = QMessageBox.question(parent, 'Question', text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.No:
        return False
    else:
        return True



class PageInit(QWizardPage):


    def __init__(self, config: Config, font: QFont, image: QPixmap, logger=None):

        super().__init__()  

        self.logger = logger

        self.setFont(font)
        self.setTitle('<font size="+2">Karte Einstecken</font>')
        self.setSubTitle('<font size="+2">Stecke die SD Karte in den Kartenleser (siehe Bilder).</font>')

        layout = QVBoxLayout()

        label = QLabel()     
        label.setPixmap(image)
        layout.addWidget(label)
            
        self.setLayout(layout)


class PageSelectAudiobook(QWizardPage):
    

    def __init__(self, config: Config, font: QFont, logger=None):

        super().__init__()  

        self.logger = logger

        self.setTitle('<font size="+2">Wähle Titel</font>')
        self.setSubTitle('<font size="+2">Wähle aus der Liste das Audiobuch, das du kopieren möchtest (Tipp: benutze das Suchfeld zum Filtern)</font>')
        self.setFont(font)
        self.config = config

        self.database = Database(logger=self.logger)
        self.database.open(DBFILE)

        self.scanner = Scanner(self.config, self.database, logger=self.logger)
        playlists = self.scanner.scan() 
        
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

    def __init__(self, config: Config, font: QFont, logger=None):

        super().__init__()  

        self.logger = logger
        
        self.setTitle('<font size="+2">Wähle Ziel</font>')   
        self.setSubTitle('<font size="+2">Wähle den Ort, an den das Audiobuch kopiert werden soll (existierende Dateien werden ggfs gelöscht)</font>')
        self.setFont(font)  
        self.config = config

        self.label = QLabel('')
        self.label.setFont(font)

        self.log = Log()
        self.log.console.setFont(font)

        self.comboBoxDisk = QComboBox()
        self.comboBoxDisk.setFont(font)
        self.comboBoxDisk.currentTextChanged.connect(self.comboboxChanged)

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
                self.label.setText ('<font color="red">WARNING: ' + str(len(self.files)) + ' Dateien werden gelöscht</font>')   
            else:
                self.label.setText ('Keine Dateien werden gelöscht')   

            for file in self.files:
                self.log.print(file)


    def initializePage(self):

        self.comboBoxDisk.addItems(self.disks(removeableonly=True))


    def isComplete(self):

        root = self.comboBoxDisk.currentText()
    
        if root and os.path.exists(root):
            self.config.exportDir = root
            return True

        return False


    def validatePage(self):

        return self.clear() and self.copyFirst()
        
        
    def clear(self):

        root = self.config.exportDir
    
        try:

            for file in self.files:
                tools.info('delete ' + os.path.join(root, file), self.logger)        
                os.remove(os.path.join(root, file))     

        except Exception as ex:

            tools.error(str(ex), self.logger)
            QMessageBox.warning(self, 'Error', str(ex))

            return False

        return True


    def copyFirst(self):

        try:

            root = self.config.exportDir
            if os.path.exists(root):
                playlist = self.config.playlist
                if playlist and playlist.files:

                    file = playlist.files[0]
                    src = os.path.join(playlist.rootDir, playlist.bookDir, file)            
                    dst = os.path.join(root, file)
                    tools.info('copy ' + src + ' > ' + dst, self.logger)
                    tools.copyfile(src, dst)

        except Exception as ex:

                tools.error(ex, self.logger)
                QMessageBox.warning(self, 'Error', str(ex))            

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


class PageCopyFiles(QWizardPage):


    def __init__(self, config: Config, font: QFont, image: QPixmap, logger=None):

        super().__init__()  

        self.logger = logger

        self.setTitle('<font size="+2">Kopiere alle Dateien</font>')
        self.setSubTitle('<font size="+2">Führe die Schritte auf den Bildern durch und klicke dann auf "Next".')
        self.setFont(font)
        self.config = config

        layout = QVBoxLayout()

        label = QLabel()     
        label.setPixmap(image)
        layout.addWidget(label)

        label = QLabel()
        label.setFont(font)
        label.setText('Kopierfortschritt:')
        layout.addWidget(label)
        self.progressBar = QProgressBar()
        layout.addWidget(self.progressBar)
            
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
                    files = playlist.files
                    self.copyPlaylist(playlist, root, logger=self.logger)

        except Exception as ex:

                tools.error(ex, self.logger)
                QMessageBox.warning(self, 'Error', str(ex))            

                return False

        return True


    def copyPlaylist(self, playlist, root, logger=None): 

        n_files = len(playlist.files)
        self.progressBar.setMaximum(n_files)

        for i, file in enumerate(playlist.files):                      

            src = os.path.join(playlist.rootDir, playlist.bookDir, file)            
            dst = os.path.join(root, file)
        
            tools.info('copy ' + src + ' > ' + dst, logger)
            
            self.progressBar.setValue(i)
            self.progressBar.update()  
            
            tools.copyfile(src, dst)

        self.progressBar.setValue(n_files)


class PageFinal(QWizardPage):


    def __init__(self, config: Config, font: QFont, image: QPixmap, logger=None):

        super().__init__()  

        self.logger = logger

        self.setFont(font)
        self.setTitle('<font size="+2">Fertig!</font>')
        self.setSubTitle('<font size="+2">Das Audiobuch wurde erfolgreiche kopiert. Viel Spaß beim Hören.</font>')

        layout = QVBoxLayout()

        label = QLabel()     
        label.setPixmap(image)
        layout.addWidget(label)
            
        self.setLayout(layout)


class Export(QWizard):

    def __init__(self, parent = None):

        super().__init__()  

        # logger

        self.logger = logging.getLogger('pyabp')
        logFileHandler = logging.FileHandler(LOGFILE)
        logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        logFileHandler.setFormatter(logFormatter)
        self.logger.addHandler(logFileHandler) 
        self.logger.setLevel(logging.DEBUG)

        # config

        self.readConfig()    
        font = QFont()
        font.setPixelSize(self.config.fontSize)

        # window

        rect = QDesktopWidget().screenGeometry(-1)
        #width = rect.width() * 0.75;
        width = 885
        #height = rect.height() * 0.75;
        height = 700        
        left = (rect.width() - width) / 2
        top = (rect.height() - height) / 2
        self.setGeometry(left, top, width, height) 

        self.parent = parent
        self.setWindowTitle(TITLE)
        self.setWindowIcon(QIcon(ICONFILE))

        image = QPixmap('../pics/export1.png')
        self.addPage(PageInit(self.config, font, image, logger=self.logger)) 
        self.addPage(PageSelectAudiobook(self.config, font, logger=self.logger))
        self.addPage(PageSelectDrive(self.config, font, logger=self.logger))
        image = QPixmap('../pics/export2.png')  
        self.addPage(PageCopyFiles(self.config, font, image, logger=self.logger))        
        image = QPixmap('../pics/export3.png')  
        self.addPage(PageFinal(self.config, font, image, logger=self.logger))

        self.show()    


    def readConfig(self):
        
        self.config = Config(logger=self.logger)

        if os.path.exists(CONFFILE):            
            self.config.read(CONFFILE)   

        tools.info('-'*30, self.logger)
        self.config.print(logger=self.logger)       
        tools.info('-'*30, self.logger)


if __name__ == '__main__':    

    app = QApplication(sys.argv)
    ex = Export()
    sys.exit(app.exec_())    
   
