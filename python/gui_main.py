import sys
import os
import warnings
import shutil
import glob

from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime, QEvent)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QPushButton, QGridLayout, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QTreeView, QVBoxLayout, QWidget, QAbstractItemView, QMessageBox, qApp)

import tools
from player import Player
from playlist import Playlist
from scanner import Scanner
from config import Config

from gui_library import Library
from gui_control import Control
from gui_control_thread import ControlThread
 

CONFFILE = 'pyabp.init'
TITLE = 'Python Audiobook Player'
ICONFILE = '../pics/player.ico'


class App(QWidget):
 

    config = None
    font = None
    scanner = None
    player = None
    library = None
    control = None
    controlThread = None    
    layout = None      


    def __init__(self, root, ext='.mp3', force=False):

        super().__init__()    

        # event filter

        qApp.installEventFilter(self) 

        # config

        self.readConfig()

        # player    

        self.player = Player()
        self.player.connect(root)
        self.player.update()

        # playlists

        self.scanner = Scanner()
        playlists = self.scanner.scan(root, ext=ext, force=force)

        # init

        self.initUI(playlists)     

        # play

        if os.path.exists(self.config.currentPath):
            for playlist in playlists:
                if playlist.root == self.config.currentPath:
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
        self.library.rescanButton.clicked.connect(self.rescanClicked)   
        if os.path.exists(self.config.exportPath):
            self.library.rootLineEdit.setText(self.config.exportPath)  
        self.library.setVisible(False)       

        # control

        self.control = Control(font=font)
        self.control.libraryButton.clicked.connect(self.showFull)
        self.control.restartButton.clicked.connect(self.player.restart)
        self.control.previousButton.clicked.connect(self.player.previous)
        self.control.playButton.clicked.connect(self.player.play)        
        self.control.stopButton.clicked.connect(self.player.stop)
        self.control.nextButton.clicked.connect(self.player.next)
        self.control.volumeSlider.valueChanged.connect(self.volumeChanged)
        self.control.trackPositionSlider.sliderMoved.connect(self.positionChanged)
        self.controlThread = ControlThread(self.player, self.control)               

        # main
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.library)     
        self.layout.addWidget(self.control)
        self.setLayout(self.layout)   

        # show

        self.setFixedSize(self.layout.sizeHint())
        self.setWindowState(Qt.WindowNoState)   
        self.show()               
        if self.config.fullScreen:
            self.showFull()    
      

    def showFull(self):
        
        isVisible = self.library.isVisible()
        self.library.setVisible(not isVisible)
        if isVisible:
            self.setFixedSize(self.layout.sizeHint())
            self.setWindowState(Qt.WindowNoState) 
        else:
            self.setWindowState(Qt.WindowFullScreen)             


    def eventFilter(self, source, event):

        if event.type() == QEvent.KeyPress:
           
            if event.key() == Qt.Key_Space and not self.library.isVisible():
                self.player.toggle()
                return 1

            elif event.key() == Qt.Key_Escape:
                self.close()
                return 1

        return QWidget.eventFilter(self, source, event)


    def closeEvent(self, event):        

        if self.player:        
            self.player.close()

        self.writeConfig()

        event.accept()         


    def readConfig(self):
        
        self.config = Config()

        if os.path.exists(CONFFILE):            
            self.config.read(CONFFILE)          


    def writeConfig(self):
        
        if self.player.playlist:
            self.config.currentPath = self.player.playlist.root

        self.config.exportPath = self.library.rootLineEdit.text()            
        self.config.isPlaying = self.player.isPlay
        self.config.fullScreen = self.library.isVisible()    
        
        self.config.write(CONFFILE)


    def loadPlaylist(self, playlist, play):
        
        playlist.print()
        self.player.load(playlist)   
        self.control.volumeSlider.setValue(playlist.meta.volume)
        self.setWindowTitle(TITLE + ' [ ' + playlist.meta.artist + ' - ' + playlist.meta.album + ' ]') 
        if play:
            self.player.play()   
 

    def libraryClicked(self, index):

        playlist = self.library.getPlaylist()                
        self.loadPlaylist(playlist, False)


    def volumeChanged(self, value):
        
        self.player.volume(value)


    def positionChanged(self, value):
        
        self.player.move(value)


    def exportClicked(self):

        root = self.library.rootLineEdit.text()
        if os.path.exists(root):
            playlist = self.library.getPlaylist()
            if playlist:            
                print('-'*30)
                files = glob.glob(os.path.join(root, 'pyabp*'))
                count = 1
                if len(files) > 0:
                    reply = tools.askUser('Delete existing playlist (otherwise files are appended)?', self)
                    if not reply:
                        count = len(files) + 1
                    else:                    
                        for file in files:
                            print('delete ' + file)
                            os.remove(file) 

                playlist.export(root, count)


    def rescanClicked(self):
        
        playlist = self.library.getPlaylist()
        if playlist:
            self.scanner.scandir(playlist.root, playlist.ext, True)

 
if __name__ == '__main__':

    root = tools.getroot()  
    
    app = QApplication(sys.argv)
    ex = App(root)
    sys.exit(app.exec_())
