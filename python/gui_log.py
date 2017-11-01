import sys
import psutil
import os
import shutil

from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (Qt, QTime, QEvent, QRect)
from PyQt5.QtWidgets import (QApplication, QWidget, QPlainTextEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QLayout)

class Log(QWidget):


    def __init__(self, parent = None):

        super().__init__()  

        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.console)       

        self.setLayout(layout)

        
    def print(self, text = ''):
    
        self.console.appendPlainText(text)
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum());
        self.repaint()