import sys
import os
import warnings

from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QPushButton, QSlider, QGridLayout, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QTreeView, QVBoxLayout, QWidget, QAbstractItemView)

import tools

 
class Control(QGroupBox):
 

    trackPathLabel = None
    trackNumberLabel = None
    trackPositionSlider = None
    trackDurationLabel = None

    restartButton = None
    previousButton = None
    playButton = None
    stopButton = None
    nextButton = None
    libraryButton = None

    volumeIcon = None
    volumeSlider = None

 
    def __init__(self, fontSize = 16):

        super().__init__()              

        self.initUI(fontSize)     


    def initUI(self, fontSize):

        font = QFont()
        font.setPixelSize(fontSize)
       
        layout_top = QHBoxLayout()
        layout_center = QHBoxLayout()
        layout_bottom = QHBoxLayout()
        
        self.trackPathLabel = self.addLabel('', font, layout_top)        
        self.trackNumberLabel = self.addLabel('0/0', font, layout_center)

        self.trackPositionSlider = QSlider(Qt.Horizontal)
        layout_center.addWidget(self.trackPositionSlider)

        self.trackDurationLabel = self.addLabel(tools.friendlytime(0), font, layout_center)

        self.libraryButton = self.addButton('../pics/list.png', layout_bottom)        
        self.previousButton = self.addButton('../pics/previous.png', layout_bottom)
        self.playButton = self.addButton('../pics/play.png', layout_bottom)
        self.stopButton = self.addButton('../pics/pause.png', layout_bottom)
        self.nextButton = self.addButton('../pics/next.png', layout_bottom)        
        self.restartButton = self.addButton('../pics/restart.png', layout_bottom)

        self.volumeIcon = self.addIcon('../pics/volume.png', layout_bottom)        
        self.volumeSlider = QSlider(Qt.Horizontal)  
        self.volumeSlider.setFixedWidth(75)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setSingleStep(10)
        layout_bottom.addWidget(self.volumeSlider)

        layout = QVBoxLayout()
        layout.addLayout(layout_top)
        layout.addLayout(layout_center)
        layout.addLayout(layout_bottom)
        self.setLayout(layout)        


    def addLabel(self, text, font, layout):
        
        label = QLabel(text)        
        label.setFont(font)
        layout.addWidget(label)

        return label


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


    def addButton(self, path, layout):

        button = QPushButton()
        icon = QIcon(path)        
        button.setIcon(icon)
        size = icon.availableSizes()[0]
        button.setFixedHeight(size.height())
        button.setIconSize(size)
        layout.addWidget(button)

        return button


    def update(self, info):

        (track, length, position, duration, path) = info

        if track >= 0:
            self.trackPathLabel.setText(os.path.basename(path))
            self.trackPathLabel.setToolTip(path)
            self.trackNumberLabel.setText(str(track+1) + ' / ' + str(length))               
            self.trackPositionSlider.setMaximum(int(duration))
            self.trackPositionSlider.setValue(int(position))          
            self.trackDurationLabel.setText(tools.friendlytime(duration))  
    




 