import sys
import os
import warnings

from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QPushButton, QGridLayout, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QTreeView, QVBoxLayout, QWidget, QAbstractItemView)

from playlist import Playlist
import tools

 
class Library(QGroupBox):
 

    PLAYLIST, ARTIST, ALBUM, NTRACKS, DURATION = range(5)

    view = None
    rescanButton = None
    exportButton = None    
    rootLineEdit = None
 
    def __init__(self, playlists, fontSize = 16):

        super().__init__()              

        self.initUI(playlists, fontSize)     
        

    def initUI(self, playlists, fontSize):
        
        font = QFont()
        font.setPixelSize(fontSize)

        model = QStandardItemModel(0, 5, self)
        model.setHeaderData(self.PLAYLIST, Qt.Horizontal, "Playlist")
        model.setHeaderData(self.ARTIST, Qt.Horizontal, "Autor")
        model.setHeaderData(self.ALBUM, Qt.Horizontal, "Album")        
        model.setHeaderData(self.NTRACKS, Qt.Horizontal, "#")        
        model.setHeaderData(self.DURATION, Qt.Horizontal, "Dauer")                  
        for playlist in playlists:                                       
            model.insertRow(0)
            model.setData(model.index(0, self.PLAYLIST), playlist)
            model.setData(model.index(0, self.ARTIST), playlist.meta.artist)
            model.setData(model.index(0, self.ALBUM), playlist.meta.album)
            model.setData(model.index(0, self.NTRACKS), playlist.meta.ntracks)
            model.setData(model.index(0, self.DURATION), tools.friendlytime(playlist.meta.duration)) 

        view = QTreeView()        
        view.setFont(font)
        view.setRootIsDecorated(False)
        view.setAlternatingRowColors(True)
        view.setSortingEnabled(True)        
        view.setEditTriggers(QAbstractItemView.NoEditTriggers)                    
        view.setModel(model)                   
        for i in range(model.columnCount()-1,0,-1):
            view.sortByColumn(i, Qt.AscendingOrder)     
            view.resizeColumnToContents(i)
        view.hideColumn(0)      

        self.rescanButton = QPushButton('RESCAN')        
        self.rescanButton.setFont(font)
        self.exportButton = QPushButton('EXPORT')        
        self.exportButton.setFont(font)
        self.rootLineEdit = QLineEdit('')        
        self.rootLineEdit.setFont(font)                

        layout_bottom = QHBoxLayout()
        layout_bottom.addWidget(self.rescanButton)
        layout_bottom.addWidget(self.exportButton)
        layout_bottom.addWidget(self.rootLineEdit)

        layout = QVBoxLayout()
        layout.addWidget(view)
        layout.addLayout(layout_bottom)

        self.setLayout(layout)

        self.view = view

    
    def getPlaylist(self):
        
        indices = self.view.selectedIndexes()
        if len(indices) == 0:
            return None
        index = indices[0].row()
        item = self.view.model().item(index)
        playlist = item.data(0)

        return playlist
