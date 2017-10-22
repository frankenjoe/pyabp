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
from server import Server

from gui_library import Library
from gui_control import Control
from gui_control_thread import ControlThread
 

CONFFILE = '../pyabp.init'
TITLE = 'Python Audiobook Player'
ICONFILE = '../pics/player.ico'


class App(QWidget):
 

    config = None
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

        # event filter

        qApp.installEventFilter(self) 

        # config

        self.readConfig()
        
        # mpd

        if self.config.startMpd:
            self.server = Server()
            self.server.start('..\\mpd\\mpd.exe', conf=os.path.realpath(self.config.confPath))

        # player    

        self.player = Player()
        self.player.connect()
        self.player.update()

        # playlists

        self.scanner = Scanner()
        playlists = self.scanner.scan(self.config)

        # init

        self.initUI(playlists)     

        # play

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
        if os.path.exists(self.config.exportDir):
            self.library.exportLineEdit.setText(self.config.exportDir)  
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
        self.control.trackPositionSlider.setTracking(False)
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
           
            if event.key() == Qt.Key_Space and not self.library.searchLineEdit.hasFocus() and not self.library.exportLineEdit.hasFocus():
                self.player.toggle()
                return 1

            elif event.key() == Qt.Key_Escape:
                self.close()
                return 1

        return QWidget.eventFilter(self, source, event)


    def closeEvent(self, event):        

        self.writeConfig()
      
        self.player.close()
        if self.server:
            self.server.stop()

        event.accept()         


    def readConfig(self):
        
        self.config = Config()

        if os.path.exists(CONFFILE):            
            self.config.read(CONFFILE)   

        print('-'*30)
        self.config.print()       
        print('-'*30)
        

    def writeConfig(self):
        
        if self.player.playlist:
            self.config.lastDir = self.player.playlist.bookDir

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
        if playlist:               
            self.loadPlaylist(playlist, self.player.isPlay)


    def volumeChanged(self, value):
        
        self.player.volume(value)


    def positionChanged(self, value):
        
        self.player.move(value)


    def exportClicked(self):

        root = self.config.exportDir
        if os.path.exists(root):
            playlist = self.library.getPlaylist()
            if playlist:            
                print('-'*30)
                files = glob.glob(os.path.join(root, 'pyabp*'))
                count = 1
                if len(files) > 0:
                    reply = self.askUser('Delete existing playlist (otherwise files are appended)?')
                    if not reply:
                        count = len(files) + 1
                    else:                    
                        for file in files:
                            print('delete ' + file)
                            os.remove(file) 

                playlist.export(root, count)


    def askUser(self, text):

        reply = QMessageBox.question(self, 'Question', text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return False
        else:
            return True

 
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

    tools.procstop(pid)
