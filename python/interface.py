import sys
import os
import warnings

from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QTreeView, QVBoxLayout, QWidget, QAbstractItemView)

import tools
from player import Player
from playlist import Playlist
from scanner import Scanner

 
class App(QWidget):
 

    PLAYLIST, ARTIST, ALBUM, NTRACKS, DURATION = range(5)
 
    player = None
    playlists = []

    def __init__(self, root, ext='.mp3', force=False):

        super().__init__()        

        self.player = Player()
        self.player.connect(root)
        self.player.update()

        scanner = Scanner()
        self.playlists = scanner.scan(root, ext=ext, force=force)

        self.initUI()     
        

    def initUI(self):

        self.setWindowTitle('Audiobook Player')
        self.setWindowState(Qt.WindowMaximized)
 
        self.dataGroupBox = QGroupBox('Bibliothek')
        self.dataView = QTreeView()
        font = QFont()
        font.setPixelSize(16);
        self.dataView.setFont(font);        
        self.dataView.setRootIsDecorated(False)
        self.dataView.setAlternatingRowColors(True)
        self.dataView.setSortingEnabled(True)        
        self.dataView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dataView.doubleClicked.connect(self.treeDoubleClicked)
 
        dataLayout = QHBoxLayout()
        dataLayout.addWidget(self.dataView)
        self.dataGroupBox.setLayout(dataLayout)
 
        model = self.createPlaylistModel(self)          
        self.dataView.setModel(model)                   

        for playlist in self.playlists:                                       
            self.addPlaylist(model, playlist)                        
        for i in range(model.columnCount()-1,0,-1):
            self.dataView.sortByColumn(i, Qt.AscendingOrder)     
            self.dataView.resizeColumnToContents(i)
        self.dataView.hideColumn(0)
 
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.dataGroupBox)
        self.setLayout(mainLayout)    
 
        self.show()
 

    def closeEvent(self, event):

        if self.player:
            self.player.close()
        event.accept()


    def createPlaylistModel(self,parent):

        model = QStandardItemModel(0, 5, parent)
        model.setHeaderData(self.PLAYLIST, Qt.Horizontal, "Playlist")
        model.setHeaderData(self.ARTIST, Qt.Horizontal, "Autor")
        model.setHeaderData(self.ALBUM, Qt.Horizontal, "Album")        
        model.setHeaderData(self.NTRACKS, Qt.Horizontal, "#")        
        model.setHeaderData(self.DURATION, Qt.Horizontal, "Dauer")        
        return model

 
    def addPlaylist(self, model, playlist):

        model.insertRow(0)
        model.setData(model.index(0, self.PLAYLIST), playlist)
        model.setData(model.index(0, self.ARTIST), playlist.meta.artist)
        model.setData(model.index(0, self.ALBUM), playlist.meta.album)
        model.setData(model.index(0, self.NTRACKS), playlist.meta.ntracks)
        model.setData(model.index(0, self.DURATION), playlist.meta.durationstr())


    def treeDoubleClicked(self,index):

        item = self.dataView.model().item(index.row(),0)                
        playlist = item.data(0)
        playlist.print()
        self.player.load(playlist)
        self.player.play()

 
if __name__ == '__main__':

    root = tools.getroot()  
    
    app = QApplication(sys.argv)
    ex = App(root)
    sys.exit(app.exec_())
