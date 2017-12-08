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
import define

from player import Player
from playlist import Playlist
from scanner import Scanner
from config import Config
from server import Server
from database import Database

from gui_init import Init
from gui_library import Library
from gui_control import Control
from gui_control_thread import ControlThread
 

class Main(QWidget):
 

    logger = None
    config = None
    database = None
    font = None    
    server = None
    player = None
    library = None
    control = None
    controlThread = None    
    layout = None


    def __init__(self, app, config, server, player, playlists, logger=None):

        super().__init__()    

        # logger

        self.logger = logger

        # event filter

        qApp.installEventFilter(self) 

        # init
        
        self.config = config
        self.server = server
        self.player = player
        self.initUI(playlists)    

        # load playlist

        if os.path.exists(os.path.join(self.config.rootDir, self.config.lastDir)):
            for playlist in playlists:
                if playlist.bookDir == self.config.lastDir:
                    self.loadPlaylist(playlist, self.config.isPlaying)                    
                    break  
        

    def initUI(self, playlists):

        self.setWindowTitle(define.TITLE)
        self.setWindowIcon(QIcon(define.ICONFILE))

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
        self.control.restartButton.clicked.connect(self.onRestart)
        self.control.previousButton.clicked.connect(self.onPrevious)
        self.control.playButton.clicked.connect(self.onPlay)        
        self.control.stopButton.clicked.connect(self.onStop)
        self.control.nextButton.clicked.connect(self.onNext)
        self.control.volumeSlider.valueChanged.connect(self.onVolumeChanged)
        self.control.trackPositionSlider.sliderMoved.connect(self.onPositionChanged)
        self.control.trackPositionSlider.setTracking(False)
        self.controlThread = ControlThread(self.player, self.control)               

        # main
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.library)     
        self.layout.addWidget(self.control)
        self.setLayout(self.layout)   

        # show
        
        #self.setWindowState(Qt.WindowNoState)
        #self.setWindowFlags(
        #    Qt.Window |
        #    Qt.CustomizeWindowHint |
        #    Qt.WindowTitleHint |
        #    Qt.WindowCloseButtonHint |
        #    Qt.WindowMinimizeButtonHint |
        #    Qt.WindowStaysOnTopHint
        #)        
        self.layout.setSizeConstraint(QLayout.SetFixedSize | QLayout.SetMinimumSize)          
        self.show()               
        if self.config.fullScreen:
            self.showLibrary()    
      

    def showLibrary(self):
        
        isVisible = not self.library.isVisible()
        self.library.setVisible(isVisible)
        if not isVisible:                       
            #self.setWindowState(Qt.WindowNoState) 
            #self.setWindowFlags(
            #    Qt.Window |
            #    Qt.CustomizeWindowHint |
            #    Qt.WindowTitleHint |
            #    Qt.WindowCloseButtonHint |
            #    Qt.WindowMinimizeButtonHint |
            #    Qt.WindowStaysOnTopHint
            #)  
            self.layout.setSizeConstraint(QLayout.SetFixedSize | QLayout.SetMinimumSize)
            self.setFixedSize(self.layout.sizeHint())            
        else:                        
            #self.setWindowState(Qt.WindowMaximized)       
            #self.setWindowFlags(
            #    Qt.Window |
            #    Qt.CustomizeWindowHint |
            #    Qt.WindowTitleHint |
            #    Qt.WindowCloseButtonHint |
            #    Qt.WindowFullscreenButtonHint |
            #    Qt.WindowMinimizeButtonHint |
            #    Qt.WindowStaysOnTopHint
            #)      
            self.layout.setSizeConstraint(QLayout.SetMaximumSize)
            #self.setFixedSize(self.layout.sizeHint()) 


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

        if self.player.playlist:            
            self.config.lastDir = self.player.playlist.bookDir
        self.config.isPlaying = self.player.isPlay
        self.config.fullScreen = self.library.isVisible()   

        tools.writeConfig(self.config, define.CONFFILE,logger=self.logger)
      
        self.player.close()
        if self.server:
            self.server.stop()
        if self.database:
            self.database.close()

        event.accept()         


    def loadPlaylist(self, playlist, play):
        
        playlist.print(logger=self.logger)
        self.player.load(playlist)   
        self.control.volumeSlider.setValue(playlist.meta.volume)        
        self.setWindowTitle(define.TITLE + ' [ ' + playlist.meta.artist + ' - ' + playlist.meta.album + ' ]') 
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


    def onPlay(self):
        self.player.play()  


    def onStop(self):
        self.player.stop()


    def onNext(self):
        self.player.next()  


    def onPrevious(self):
        self.player.previous()  


    def onRestart(self):
        self.player.restart()  


    def onVolumeChanged(self, value):
        
        self.player.volume(value)


    def onPositionChanged(self, value):
        
        self.player.move(value)



 
if __name__ == '__main__':

    # logger

    logger = logging.getLogger('pyabp')
    logFileHandler = logging.FileHandler(define.LOGFILE)
    logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logFileHandler.setFormatter(logFormatter)
    logger.addHandler(logFileHandler) 
    logger.setLevel(logging.DEBUG)

    # config

    config = tools.readConfig(define.CONFFILE,logger=None) 

    # run

    app = QApplication(sys.argv)
    init = Init(app, config, logger=logger)
    init.hide()  
    main = Main(app, config, init.server, init.player, init.playlists, logger=logger)    
    sys.exit(app.exec_())
