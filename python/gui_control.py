import sys
import os
import warnings

from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QPushButton, QGridLayout, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QTreeView, QVBoxLayout, QWidget, QAbstractItemView)

 
class Control(QGroupBox):
 

    PLAYLIST, ARTIST, ALBUM, NTRACKS, DURATION = range(5)

    restartButton = None
    previousButton = None
    toggleButton = None
    stopButton = None
    nextButton = None

 
    def __init__(self):

        super().__init__('Control')              

        self.initUI()     
        

    def initUI(self):

        layout = QHBoxLayout()
        
        trackLabel = QLabel('0/0')
        layout.addWidget(trackLabel, alignment=Qt.AlignRight)

        self.restartButton = QPushButton('Restart')
        layout.addWidget(self.restartButton)

        self.previousButton = QPushButton('Previous')
        layout.addWidget(self.previousButton)

        self.toggleButton = QPushButton('Toggle')
        layout.addWidget(self.toggleButton)

        self.stopButton = QPushButton('Stop')
        layout.addWidget(self.stopButton)

        self.nextButton = QPushButton('Next')
        layout.addWidget(self.nextButton)

        self.setLayout(layout)






 