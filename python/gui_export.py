import sys
import psutil
import os
import shutil
import logging
import time
from threading import Thread

from PyQt5.QtGui import (QIcon, QFont, QPixmap)
from PyQt5.QtCore import (Qt, QTime, QEvent, QRect)
from PyQt5.QtWidgets import (QApplication, QWidget, QDesktopWidget, QWizard, QWizardPage, QProgressBar, QComboBox, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QLayout, QMessageBox, QSizePolicy)

import tools
import define
from gui_library import Library
from playlist import Playlist
from config import Config
from scanner import Scanner
from gui_log import Log
from database import Database


TITLE = 'Kopiere Hörbuch'


def askUser(parent: QWidget, text: str):

    reply = QMessageBox.question(parent, 'Question', text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.No:
        return False
    else:
        return True



class PageInit(QWizardPage):


    thread = None


    def __init__(self, wizard, config: Config, font: QFont, image: QPixmap, logger=None):

        super().__init__()  

        self.wizard = wizard
        self.logger = logger
        self.config = config

        self.setFont(font)
        self.setTitle('<font size="+2">Karte Einstecken</font>')
        self.setSubTitle('<font size="+2">Karte aus Lautsprecher in den Computer.</font>')

        layout = QVBoxLayout()

        label = QLabel()     
        label.setPixmap(image)
        label.setContentsMargins(0,20,0,0)
        layout.addWidget(label)
            
        self.setLayout(layout)             
        
        
    def initializePage(self):
    
        tools.info('*** connect drive')    
        self.isComplete = False
        
            
    def validatePage(self):

        return True            

    
    def isComplete(self):
        
        if self.isComplete:
            return True

        name = self.config.driveName
        
        tools.info('look for drive "' + name + '"', logger=self.logger)
        
        drive = tools.drivebyname(name)
        if drive:                
            tools.info('set export directory to "' + drive + '"', logger=self.logger)   
            self.config.exportDir = drive   
            self.isComplete = True
            self.wizard.next()
            return True
              
        thread = Thread(target=self.waitForDrive, args=(self.completeChanged,name,), daemon=True)        
        thread.start()      

        return False


    def waitForDrive(self, completeChanged, driveName):            
       
        while not tools.drivebyname(driveName):            
            tools.info('wait for drive "' + driveName + '"', logger=self.logger)            
            time.sleep(1) 

        completeChanged.emit()    
        


class PageSelectAudiobook(QWizardPage):
    

    def __init__(self, wizard, config: Config, font: QFont, logger=None):

        super().__init__()  

        self.wizard = wizard
        self.logger = logger

        self.setTitle('<font size="+2">Wähle Titel</font>')
        self.setSubTitle('<font size="+2">Hörbuch aus Liste wählen. (Tipp: benutze Suchfeld zum Filtern)</font>')
        self.setFont(font)
        self.config = config

        self.database = Database(logger=self.logger)
        self.database.open(define.DBFILE)

        self.scanner = Scanner(self.config, self.database, logger=self.logger)
        playlists = self.scanner.scan() 
        
        self.library = Library(playlists, font=font)
        self.library.view.clicked.connect(self.libraryClicked) 

        layout = QVBoxLayout()        
        layout.addWidget(self.library)
        self.setLayout(layout)

        
    def initializePage(self):
    
        tools.info('*** select audiobook')   
        self.isComplete = False         
        
        
    def validatePage(self):

        return True


    def isComplete(self):
        
        if self.isComplete:
            return True           

        playlist = self.library.getPlaylist()
        print(playlist)

        if playlist:
            self.config.playlist = playlist
            self.isComplete = True
            self.wizard.next()                     
            return True

        return False


    def libraryClicked(self, index):

        self.completeChanged.emit()


class PagePrepareDrive(QWizardPage):

    def __init__(self, wizard, config: Config, font: QFont, image: QPixmap, logger=None):

        super().__init__()  

        self.wizard = wizard
        self.logger = logger
        
        self.setTitle('<font size="+2">Kopiere erste Datei</font>')   
        self.setSubTitle('<font size="+2">Speicherkarte aus Computer in Lautsprecher und diesen einschalten.</font>')
        self.setFont(font)  
        self.config = config

        layout = QVBoxLayout()

        label = QLabel()     
        label.setContentsMargins(0,20,0,0)
        label.setPixmap(image)
        layout.addWidget(label)
 
        self.setLayout(layout)     


    def initializePage(self):
    
        tools.info('*** pepare drive')                
        self.isComplete = False  
        self.threadIsRunning = False         
        
        self.clear() and self.copyFirst()
        
        
    def validatePage(self):

        return True        


    def isComplete(self):
        
        if self.isComplete:
            return True        

        name = self.config.driveName
        
        tools.info('look for drive "' + name + '"', logger=self.logger) 
        
        drive = tools.drivebyname(name)
        if not drive:                            
            tools.info('drive "' + name + '" has been removed', logger=self.logger)            
            self.isComplete = True
            self.wizard.next()                        
            return True            
              
        if not self.threadIsRunning:
              
            self.threadIsRunning = True
            thread = Thread(target=self.waitForRemoveDrive, args=(self.completeChanged,name,), daemon=True)        
            thread.start()      

        return False


    def waitForRemoveDrive(self, completeChanged, driveName):            
        
        tools.info('start thread')
       
        while tools.drivebyname(driveName):            
            tools.info('wait for drive "' + driveName + '" to be removed', logger=self.logger)            
            time.sleep(1) 

        completeChanged.emit()    
        
        tools.info('stop thread')


    def validatePage(self):

        return True
        
        
    def clear(self):

        root = self.config.exportDir
    
        try:

            if os.path.exists(root):
                files = tools.getfiles(root, self.config.scanExtensions)
                if len(files) > 0:                
                    for file in files:
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


class PageCopyFiles(QWizardPage):


    def __init__(self, wizard, config: Config, font: QFont, image: QPixmap, logger=None):

        super().__init__()  

        self.wizard = wizard
        self.logger = logger

        self.setTitle('<font size="+2">Kopiere restliche Dateien</font>')
        self.setSubTitle('<font size="+2">Speicherkarte aus Lautsprecher in den Computer.')
        self.setFont(font)
        self.config = config

        layout = QVBoxLayout()

        label = QLabel()     
        label.setPixmap(image)
        label.setContentsMargins(0,20,0,20)
        layout.addWidget(label)

        label = QLabel()
        label.setFont(font)
        label.setText('Kopierfortschritt:')
        layout.addWidget(label)
        self.progressBar = QProgressBar()
        layout.addWidget(self.progressBar)
            
        self.setLayout(layout)         


    def initializePage(self):
    
        tools.info('*** copy files')
        self.isComplete = False  
        self.threadIsRunning = False          
        
        
    def validatePage(self):

        return True        

    
    def isComplete(self):

        if self.isComplete:
            return True

        name = self.config.driveName
        
        tools.info('look for drive "' + name + '"', logger=self.logger)
        
        drive = tools.drivebyname(name)
        if drive:                
            tools.info('set export directory to "' + drive + '"', logger=self.logger)   
            self.config.exportDir = drive         
            self.copy()
            self.isComplete = True
            self.wizard.next()                
            return True
              
        if not self.threadIsRunning:
            self.threadIsRunning = True
            thread = Thread(target=self.waitForDrive, args=(self.completeChanged,name,), daemon=True)        
            thread.start()      

        return False


    def waitForDrive(self, completeChanged, driveName):            
        
        tools.info('start thread')
       
        while not tools.drivebyname(driveName):            
            tools.info('wait for drive "' + driveName + '"', logger=self.logger)            
            time.sleep(1) 

        completeChanged.emit()  
        
        tools.info('stop thread')


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


    def __init__(self, wizard, config: Config, font: QFont, image: QPixmap, logger=None):

        super().__init__()  

        self.wizard = wizard
        self.logger = logger        

        self.setFont(font)
        self.setTitle('<font size="+2">Fertig!</font>')
        self.setSubTitle('<font size="+2">Das Hörbuch wurde erfolgreiche kopiert. Viel Spaß beim Hören!</font>')

        layout = QVBoxLayout()

        label = QLabel()     
        label.setContentsMargins(0,20,0,0)
        label.setPixmap(image)
        layout.addWidget(label)
            
        self.setLayout(layout)
        
        
    def initializePage(self):
    
        tools.info('*** goodbye')        


class Export(QWizard):

    def __init__(self, app, config, parent=None, logger=None):

        super().__init__()  

        # logger

        self.logger = logger

        # config

        self.config = config

        # window

        font = QFont()
        font.setPixelSize(self.config.fontSize)

        self.parent = parent
        self.setWindowTitle(TITLE)
        self.setWindowIcon(QIcon(define.ICONFILE))
        
        size = app.desktop().screenGeometry()
        self.setGeometry(0,0,size.width(),size.height())
        
        self.setButtonLayout([QWizard.Stretch, QWizard.FinishButton])

        image = QPixmap('pics/export1.png')
        self.addPage(PageInit(self, self.config, font, image, logger=self.logger)) 
        self.addPage(PageSelectAudiobook(self, self.config, font, logger=self.logger))
        image = QPixmap('pics/export2.png')
        self.addPage(PagePrepareDrive(self, self.config, font, image, logger=self.logger))
        image = QPixmap('pics/export3.png')  
        self.addPage(PageCopyFiles(self, self.config, font, image, logger=self.logger))        
        image = QPixmap('pics/export4.png')  
        self.addPage(PageFinal(self, self.config, font, image, logger=self.logger))
        
        self.showMaximized()


if __name__ == '__main__':    

    # logger

    logger = logging.getLogger('pyabp')
    logFileHandler = logging.FileHandler(define.LOGFILE)
    logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logFileHandler.setFormatter(logFormatter)
    logger.addHandler(logFileHandler) 
    logger.setLevel(logging.DEBUG)

    # config

    config = tools.readConfig(define.CONFFILE,logger=logger) 

    # run

    app = QApplication(sys.argv)    
    ex = Export(app, config, logger=logger)
    sys.exit(app.exec_())    
   
