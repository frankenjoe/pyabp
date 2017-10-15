import sys
import os
import warnings

from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QPushButton, QGridLayout, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QTreeView, QVBoxLayout, QWidget, QAbstractItemView)

from playlist import Playlist
import tools


PLAYLIST, ARTIST, ALBUM, DURATION, COLUMNS = range(5)

 
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
    model = None
    filter = None
    searchIcon = None
    searchLineEdit = None
    rescanButton = None
    exportButton = None    
    exportLineEdit = None    

 
    def __init__(self, playlists, font=QFont()):

        super().__init__()              

        self.initUI(playlists, font) 
      

    def initUI(self, playlists, font):           

        # list

        model = QStandardItemModel(0, COLUMNS, self)
        model.setHeaderData(PLAYLIST, Qt.Horizontal, "Playlist")
        model.setHeaderData(ARTIST, Qt.Horizontal, "Autor")
        model.setHeaderData(ALBUM, Qt.Horizontal, "Album")              
        model.setHeaderData(DURATION, Qt.Horizontal, "Dauer")                  
        for playlist in playlists:                                       
            model.insertRow(0)
            model.setData(model.index(0, PLAYLIST), playlist)
            model.setData(model.index(0, ARTIST), playlist.meta.artist)
            model.setData(model.index(0, ALBUM), playlist.meta.album)
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

        layout_top = QHBoxLayout()   

        self.searchIcon = self.addIcon('../pics/lense.png', layout_top)
        self.searchLineEdit = QLineEdit('')        
        self.searchLineEdit.setFont(font)                        
        self.searchLineEdit.textChanged.connect(filterModel.setFilterFixedString)
        layout_top.addWidget(self.searchLineEdit)

        # export

        layout_bottom = QHBoxLayout()

        self.rescanButton = QPushButton('RESCAN')        
        self.rescanButton.setFont(font)
        self.exportButton = QPushButton('EXPORT')        
        self.exportButton.setFont(font)
        self.exportLineEdit = QLineEdit('')        
        self.exportLineEdit.setFont(font)                

        layout_bottom.addWidget(self.rescanButton)
        layout_bottom.addWidget(self.exportButton)
        layout_bottom.addWidget(self.exportLineEdit)

        # layout

        layout = QVBoxLayout()
        layout.addLayout(layout_top)
        layout.addWidget(view)
        layout.addLayout(layout_bottom)

        self.setLayout(layout)

        self.view = view
        self.model = model
        self.filter = filterModel


    def addIcon(self, path, layout):
        
        button = QPushButton() 
        button.setFlat(True)           
        icon = QIcon(path)    
        button.setIcon(icon)
        size = icon.availableSizes()[0]
        button.setFixedSize(size)
        button.setIconSize(size)
        layout.addWidget(button)

        return button

    
    def getPlaylist(self):
        
        indices = self.view.selectedIndexes()
        if len(indices) == 0:
            return None

        index = self.filter.mapToSource(indices[0])
        item = self.model.item(index.row())
        playlist = item.data(0)

        return playlist
