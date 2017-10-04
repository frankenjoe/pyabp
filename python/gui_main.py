import sys
import os
import warnings

from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QPushButton, QGridLayout, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QTreeView, QVBoxLayout, QWidget, QAbstractItemView)

import tools
from player import Player
from playlist import Playlist
from scanner import Scanner

from gui_library import Library
from gui_control import Control
from gui_editor import Editor
 
class App(QWidget):
 

    player = None
    library = None
    control = None
    editor = None


    def __init__(self, root, ext='.mp3', force=False):

        super().__init__()        

        self.player = Player()
        self.player.connect(root)
        self.player.update()

        scanner = Scanner()
        playlists = scanner.scan(root, ext=ext, force=force)

        self.initUI(playlists)     
        

    def initUI(self, playlists):

        self.setWindowTitle('Audiobook Player')
        self.setWindowState(Qt.WindowMaximized)
 
        # library

        self.library = Library(playlists)
        self.library.view.doubleClicked.connect(self.libraryDoubleClicked)     

        # editor                

        self.editor = Editor()        

        # control

        self.control = Control()
        self.control.restartButton.clicked.connect(self.controlButtonClicked)
        self.control.previousButton.clicked.connect(self.controlButtonClicked)
        self.control.toggleButton.clicked.connect(self.controlButtonClicked)
        self.control.stopButton.clicked.connect(self.controlButtonClicked)
        self.control.nextButton.clicked.connect(self.controlButtonClicked)

        # main
 
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.library, 0, 0, 2, 1)
        mainLayout.addWidget(self.editor, 0, 1)
        mainLayout.addWidget(self.control, 1, 1)
        self.setLayout(mainLayout)    
 
        self.show()
 

    def controlButtonClicked(self):

        message = self.sender().text()
        if message == 'Restart':
            self.player.restart()
        elif message == 'Previous':
            self.player.previous()
        elif message == 'Toggle':
            self.player.toggle()
        elif message == 'Stop':
            self.player.stop()
        elif message == 'Next':
           self.player.next()
        

    def closeEvent(self, event):

        if self.player:
            self.player.close()
        event.accept()


    def libraryDoubleClicked(self, index):

        item = self.library.view.model().item(index.row(),0)                
        playlist = item.data(0)
        playlist.print()
        self.player.load(playlist)
        self.player.play()
        self.editor.setPlaylist(playlist.meta)

 
if __name__ == '__main__':

    root = tools.getroot()  
    
    app = QApplication(sys.argv)
    ex = App(root)
    sys.exit(app.exec_())
