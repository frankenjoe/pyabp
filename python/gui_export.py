import sys
import os
import warnings

from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QPushButton, QSlider, QGridLayout, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QTreeView, QVBoxLayout, QWidget, QAbstractItemView)

import tools

 
class Export(QGroupBox):
 

    exportButton = None    
    rootLineEdit = None
    
 
    def __init__(self, fontSize = 16):

        super().__init__()              

        self.initUI(fontSize)     


    def initUI(self, fontSize):

        font = QFont()
        font.setPixelSize(fontSize)
               
        self.exportButton = QPushButton('EXPORT')        
        self.exportButton.setFont(font)
        self.rootLineEdit = QLineEdit('')        
        self.rootLineEdit.setFont(font)                

        layout = QHBoxLayout()
        layout.addWidget(self.exportButton)
        layout.addWidget(self.rootLineEdit)
        self.setLayout(layout)        



            
                                   






 