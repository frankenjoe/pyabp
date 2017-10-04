import sys
import os
import warnings

from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QPushButton, QGridLayout, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QTreeView, QVBoxLayout, QWidget, QAbstractItemView)

 
from meta import Meta


class Editor(QGroupBox):
 

    PLAYLIST, ARTIST, ALBUM, NTRACKS, DURATION = range(5)

    albumEdit = None
    artistEdit = None
    contentEdit = None

 
    def __init__(self):

        super().__init__('Editor')              

        self.initUI()     
        

    def initUI(self):

        layout = QFormLayout()
        
        albumLabel = QLabel('Album')
        self.albumEdit = QLineEdit()
        layout.addRow(albumLabel, self.albumEdit)

        artistLabel = QLabel('Artist')
        self.artistEdit = QLineEdit()
        layout.addRow(artistLabel, self.artistEdit)

        contentLabel = QLabel('Content')
        self.contentEdit = QTextEdit()
        layout.addRow(contentLabel, self.contentEdit)
                        
        self.setLayout(layout)


    def setPlaylist(self, meta):
        
        self.albumEdit.setText(meta.album)
        self.artistEdit.setText(meta.artist)
        self.contentEdit.setText(meta.info)




 