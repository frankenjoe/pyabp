import sys
import os
import warnings

from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QPushButton, QGridLayout, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QTreeView, QVBoxLayout, QWidget, QAbstractItemView)

from playlist import Playlist
import tools


PLAYLIST, ARTIST, ALBUM, NTRACKS, DURATION = range(5)

 
class SortFilterProxyModel(QSortFilterProxyModel):


    def filterAcceptsRow(self, sourceRow, sourceParent):        

        pattern = self.filterRegExp().pattern()

        if pattern != '':
            
            artist = self.sourceModel().data(self.sourceModel().index(sourceRow, ARTIST, sourceParent))
            album = self.sourceModel().data(self.sourceModel().index(sourceRow, ALBUM, sourceParent))
            
            return pattern in artist.lower() or pattern in album.lower()

        else:

            #return super(SortFilterProxyModel, self).filterAcceptsRow(sourceRow, sourceParent)
            return True


class Library(QGroupBox):
     

    view = None
    filterLabel = None
    filterLineEdit = None
    rescanButton = None
    exportButton = None    
    rootLineEdit = None    

 
    def __init__(self, playlists, fontSize = 16):

        super().__init__()              

        self.initUI(playlists, fontSize) 
      

    def initUI(self, playlists, fontSize):
        
        font = QFont()
        font.setPixelSize(fontSize)        

        # list

        model = QStandardItemModel(0, 5, self)
        model.setHeaderData(PLAYLIST, Qt.Horizontal, "Playlist")
        model.setHeaderData(ARTIST, Qt.Horizontal, "Autor")
        model.setHeaderData(ALBUM, Qt.Horizontal, "Album")        
        model.setHeaderData(NTRACKS, Qt.Horizontal, "#")        
        model.setHeaderData(DURATION, Qt.Horizontal, "Dauer")                  
        for playlist in playlists:                                       
            model.insertRow(0)
            model.setData(model.index(0, PLAYLIST), playlist)
            model.setData(model.index(0, ARTIST), playlist.meta.artist)
            model.setData(model.index(0, ALBUM), playlist.meta.album)
            model.setData(model.index(0, NTRACKS), playlist.meta.ntracks)
            model.setData(model.index(0, DURATION), tools.friendlytime(playlist.meta.duration)) 

        filterModel = SortFilterProxyModel()
        filterModel.setSourceModel(model)           

        view = QTreeView()        
        view.setFont(font)
        view.setRootIsDecorated(False)
        view.setAlternatingRowColors(True)
        view.setSortingEnabled(True)        
        view.setEditTriggers(QAbstractItemView.NoEditTriggers)                    
        view.setModel(filterModel)                   
        for i in range(model.columnCount()-1,0,-1):
            view.sortByColumn(i, Qt.AscendingOrder)     
            view.resizeColumnToContents(i)
        view.hideColumn(0)      

        # filter

        self.filterLabel = QLabel('Filter')
        self.filterLabel.setFont(font)
        self.filterLineEdit = QLineEdit('')        
        self.filterLineEdit.setFont(font)                        
        self.filterLineEdit.textChanged.connect(filterModel.setFilterFixedString)

        layout_top = QHBoxLayout()
        layout_top.addWidget(self.filterLabel)
        layout_top.addWidget(self.filterLineEdit)

        # export

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

        # layout

        layout = QVBoxLayout()
        layout.addLayout(layout_top)
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
