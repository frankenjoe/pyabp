import sys
import os
import warnings
import shutil
import glob

from configparser import ConfigParser

from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime, QEvent)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QPushButton, QGridLayout, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QTreeView, QVBoxLayout, QWidget, QAbstractItemView, QMessageBox, qApp)

import tools
from player import Player
from playlist import Playlist
from scanner import Scanner

from gui_library import Library
from gui_control import Control
from gui_control_thread import ControlThread
from gui_export import Export
 
class App(QWidget):
 

    CONFFILE = 'pyabp.init'
    TITLE = 'Python Audiobook Player'

    player = None
    library = None
    control = None
    controlThread = None    
    export = None
    layout = None    


    def __init__(self, root, ext='.mp3', force=False):

        super().__init__()    

        # event filter

        qApp.installEventFilter(self) 

        # player    

        self.player = Player()
        self.player.connect(root)
        self.player.update()

        # playlists

        scanner = Scanner()
        playlists = scanner.scan(root, ext=ext, force=force)

        # init

        self.initUI(playlists)     

        # config

        self.readConfig(playlists)
        

    def initUI(self, playlists):

        self.setWindowTitle(self.TITLE)
 
        # library

        self.library = Library(playlists)
        self.library.view.doubleClicked.connect(self.libraryClicked)    
        self.library.setVisible(False)       

        # control

        self.control = Control()
        self.control.libraryButton.clicked.connect(self.showFull)
        self.control.restartButton.clicked.connect(self.player.restart)
        self.control.previousButton.clicked.connect(self.player.previous)
        self.control.playButton.clicked.connect(self.player.play)        
        self.control.stopButton.clicked.connect(self.player.stop)
        self.control.nextButton.clicked.connect(self.player.next)
        self.control.volumeSlider.valueChanged.connect(self.volumeChanged)
        self.controlThread = ControlThread(self.player, self.control)     

        # export

        self.export = Export()        
        self.export.setVisible(False) 
        self.export.exportButton.clicked.connect(self.exportClicked)             

        # main
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.library)        
        self.layout.addWidget(self.control)
        self.layout.addWidget(self.export)
        self.setLayout(self.layout)   

        # show

        self.setFixedSize(self.layout.sizeHint())
        self.setWindowState(Qt.WindowNoState)   
        self.show()        
      

    def showFull(self):
        
        isVisible = self.library.isVisible()
        self.library.setVisible(not isVisible)
        self.export.setVisible(not isVisible)
        if isVisible:
            self.setFixedSize(self.layout.sizeHint())
            self.setWindowState(Qt.WindowNoState) 
        else:
            self.setWindowState(Qt.WindowFullScreen)             


    def eventFilter(self, source, event):

        if event.type() == QEvent.KeyPress:
           
            if event.key() == Qt.Key_Space:
                self.player.toggle()
                return 1

            elif event.key() == Qt.Key_Escape:
                self.close()
                return 1

        return QWidget.eventFilter(self, source, event)


    def closeEvent(self, event):

        if self.player:        
    
            self.writeConfig()

            self.player.close()

        event.accept()         


    def readConfig(self, playlists):

        config = ConfigParser()
        if os.path.exists(self.CONFFILE):
            config.read(self.CONFFILE)
            root = config['DEFAULT']['root']
            export = config['DEFAULT']['export']
            if os.path.exists(export):
                self.export.rootLineEdit.setText(export)
            play = False if int(config['DEFAULT']['play']) <= 0 else True            
            for playlist in playlists:
                if playlist.root == root:
                    self.loadPlaylist(playlist, play=play)                    
                    break   
            full = False if int(config['DEFAULT']['full']) <= 0 else True
            if full:
                self.showFull()


    def writeConfig(self):

        config = ConfigParser()
        if self.player.playlist:
            root = self.player.playlist.root
            export = self.export.rootLineEdit.text()            
            play = 1 if self.player.isPlay else 0
            full = 1 if self.library.isVisible() else 0
            config['DEFAULT'] = { 'root' : root, 'play' : play, 'export' : export, 'full' : full }
            with open(self.CONFFILE, 'w') as fp:
                config.write(fp)

    def loadPlaylist(self, playlist, play=True):
        
        playlist.print()
        self.player.load(playlist)
        if play:
            self.player.play()       
        self.control.volumeSlider.setValue(playlist.meta.volume)
        self.setWindowTitle(self.TITLE + ' [ ' + playlist.meta.artist + ' - ' + playlist.meta.album + ' ]') 
 

    def libraryClicked(self, index):

        item = self.library.view.model().item(index.row(),0)                
        playlist = item.data(0)
        self.loadPlaylist(playlist)


    def volumeChanged(self, value):
        
        self.player.volume(value)


    def exportClicked(self):

        if not self.player.playlist:
            return

        playlist = self.player.playlist
        root = self.export.rootLineEdit.text()
        if os.path.exists(root):
            print('-'*30)
            files = glob.glob(os.path.join(root, 'pyabp*'))
            count = 1
            if len(files) > 0:
                reply = QMessageBox.question(self, 'Question', 'Delete existing playlist (otherwise files are appended)?.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    count = len(files) + 1
                else:                    
                    for file in files:
                        print('delete ' + file)
                        os.remove(file)            
            for file in playlist.files:
                src = os.path.join(playlist.root, file)
                name, ext = os.path.splitext(src)
                dst = os.path.join(root, 'pyabp' + str(count).zfill(4)) + ext
                print('copy ' + src + ' > ' + dst)
                tools.copyfile(src, dst)
                count = count + 1            

 
if __name__ == '__main__':

    root = tools.getroot()  
    
    app = QApplication(sys.argv)
    ex = App(root)
    sys.exit(app.exec_())
