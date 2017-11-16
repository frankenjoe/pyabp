import sys
import os
import warnings
import shutil
import glob
import logging

from PyQt5.QtGui import (QIcon, QFont,  QStandardItemModel)
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime, QEvent, QSize)
from PyQt5.QtWidgets import (qApp, QApplication, QCheckBox, QComboBox, QPushButton, QGridLayout, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QTreeView, QVBoxLayout, QWidget, QAbstractItemView, QMessageBox, QLayout, QFileDialog, QProgressDialog)

import tools
from player import Player
from playlist import Playlist
from scanner import Scanner
from config import Config
from server import Server
from database import Database

from gui_library import Library
from gui_control import Control
from gui_control_thread import ControlThread
 

LOGFILE = '../pyabp.log'
CONFFILE = '../pyabp.init'
DBFILE = '../pyabp.json'
MPDFILE = '..\\mpd\\mpd.exe'
TITLE = 'Python Audiobook Player'
ICONFILE = '../pics/player.ico'


class App(QWidget):
 

    logger = None
    config = None
    database = None
    font = None
    scanner = None
    server = None
    player = None
    library = None
    control = None
    controlThread = None    
    layout = None


    def __init__(self):

        super().__init__()    

        # logger

        self.logger = logging.getLogger('pyabp')
        logFileHandler = logging.FileHandler(LOGFILE)
        logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        logFileHandler.setFormatter(logFormatter)
        self.logger.addHandler(logFileHandler) 
        self.logger.setLevel(logging.DEBUG)

        # event filter

        qApp.installEventFilter(self) 

        # config

        self.readConfig()        

        # database

        self.database = Database(logger=self.logger)
        self.database.open(DBFILE)

        # scan

        self.scanner = Scanner(self.config, self.database, logger=self.logger)
        playlists = self.scanner.scan() 
      
        # mpd

        if self.config.startMpd:
            if not tools.islinux():
                self.server = Server(logger=self.logger)
                self.server.start(MPDFILE, conf=os.path.realpath(self.config.confPath)) 

        # player    

        self.player = Player(self.database, logger=self.logger)
        if self.player.connect():
            self.player.update()
        else:
            tools.error('could not connect player', self.logger)            

        # init

        self.initUI(playlists)    

        # load playlist

        if os.path.exists(os.path.join(self.config.rootDir, self.config.lastDir)):
            for playlist in playlists:
                if playlist.bookDir == self.config.lastDir:
                    self.loadPlaylist(playlist, self.config.isPlaying)                    
                    break  
        

    def initUI(self, playlists):

        self.setWindowTitle(TITLE)
        self.setWindowIcon(QIcon(ICONFILE))

        # font

        font = QFont()
        font.setPixelSize(self.config.fontSize)
 
        # library

        self.library = Library(playlists, font=font)
        self.library.view.doubleClicked.connect(self.libraryClicked)    
        self.library.exportButton.clicked.connect(self.exportClicked)         
        self.library.setVisible(False)       

        # control

        self.control = Control(font=font)
        self.control.libraryButton.clicked.connect(self.showLibrary)
        self.control.restartButton.clicked.connect(self.player.restart)
        self.control.previousButton.clicked.connect(self.player.previous)
        self.control.playButton.clicked.connect(self.player.play)        
        self.control.stopButton.clicked.connect(self.player.stop)
        self.control.nextButton.clicked.connect(self.player.next)
        self.control.volumeSlider.valueChanged.connect(self.volumeChanged)
        self.control.trackPositionSlider.sliderMoved.connect(self.positionChanged)
        self.control.trackPositionSlider.setTracking(False)
        self.controlThread = ControlThread(self.player, self.control)               

        # main
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.library)     
        self.layout.addWidget(self.control)
        self.setLayout(self.layout)   

        # show
        
        self.setWindowState(Qt.WindowNoState)
        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowStaysOnTopHint
        )        
        self.layout.setSizeConstraint(QLayout.SetFixedSize | QLayout.SetMinimumSize)          
        self.show()               
        if self.config.fullScreen:
            self.showLibrary()    
      

    def showLibrary(self):
        
        isVisible = not self.library.isVisible()
        self.library.setVisible(isVisible)
        if not isVisible:                       
            self.setWindowState(Qt.WindowNoState) 
            self.layout.setSizeConstraint(QLayout.SetFixedSize | QLayout.SetMinimumSize)
            self.setFixedSize(self.layout.sizeHint())            
        else:                        
            self.setWindowState(Qt.WindowFullScreen)             
            self.layout.setSizeConstraint(QLayout.SetMaximumSize)


    def eventFilter(self, source, event):

        if event.type() == QEvent.KeyPress:
           
            if not self.library.searchLineEdit.hasFocus():

                if event.key() == Qt.Key_Space:
                    self.player.toggle()
                    return 1

                if event.key() == Qt.Key_Return:
                    self.showLibrary()
                    return 1

                if event.key() == Qt.Key_P:
                    self.player.previous()
                    return 1

                if event.key() == Qt.Key_N:
                    self.player.next()
                    return 1

                if event.key() == Qt.Key_Plus:                    
                    value = min(self.control.volumeSlider.value()+5,100) 
                    self.control.volumeSlider.setValue(value)
                    return 1

                if event.key() == Qt.Key_Minus:
                    value = max(self.control.volumeSlider.value()-5,0)
                    self.control.volumeSlider.setValue(value)
                    return 1

            if event.key() == Qt.Key_Escape:
                self.close()
                return 1

        return QWidget.eventFilter(self, source, event)


    def closeEvent(self, event):        

        self.writeConfig()
      
        self.player.close()
        if self.server:
            self.server.stop()
        if self.database:
            self.database.close()

        event.accept()         


    def readConfig(self):
        
        self.config = Config(logger=self.logger)

        if os.path.exists(CONFFILE):            
            self.config.read(CONFFILE)   

        tools.info('-'*30, self.logger)
        self.config.print(logger=self.logger)       
        tools.info('-'*30, self.logger)
        

    def writeConfig(self):
                      
        if self.player.playlist:            
            self.config.lastDir = self.player.playlist.bookDir

        self.config.isPlaying = self.player.isPlay
        self.config.fullScreen = self.library.isVisible()    
        
        self.config.write(CONFFILE)


    def loadPlaylist(self, playlist, play):
        
        playlist.print(logger=self.logger)
        self.player.load(playlist)   
        self.control.volumeSlider.setValue(playlist.meta.volume)        
        self.setWindowTitle(TITLE + ' [ ' + playlist.meta.artist + ' - ' + playlist.meta.album + ' ]') 
        if play:
            self.player.play()   
 

    def libraryClicked(self, index):

        playlist = self.library.getPlaylist() 
        if playlist:               
            self.loadPlaylist(playlist, True)


    def exportClicked(self):
        
        playlist = self.library.getPlaylist() 

        if playlist and playlist.files:       

            try:
       
                root = str(QFileDialog.getExistingDirectory(self, "Select Directory"))        
                if not root:
                    return
       
                tools.info('export {} > {}'.format(playlist.bookDir, root), self.logger)
            
                n_files = len(playlist.files)

                progress = QProgressDialog('Copying files...', 'Cancel', 0, n_files, self);
                progress.setWindowTitle('')
                progress.setWindowModality(Qt.WindowModal);              

                for i, file in enumerate(playlist.files):

                    tools.info(file, self.logger)

                    progress.setValue(i);
                    progress.update()                    
                    if progress.wasCanceled():
                        break;

                    src = os.path.join(playlist.rootDir, playlist.bookDir, file)            
                    dst = os.path.join(root, file)

                    tools.copyfile(src, dst)                    
                            
                progress.setValue(n_files);

            except Exception as ex:
                
                tools.error(ex, self.logger)


    def volumeChanged(self, value):
        
        self.player.volume(value)


    def positionChanged(self, value):
        
        self.player.move(value)



 
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
