import sys
import os
import warnings
import shutil
import glob
import logging

from PyQt5.QtGui import (QIcon, QFont,  QStandardItemModel, QPixmap)
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime, QEvent, QSize)
from PyQt5.QtWidgets import (qApp, QApplication, QCheckBox, QComboBox, QPushButton, QGridLayout, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QTreeView, QVBoxLayout, QWidget, QAbstractItemView, QMessageBox, QLayout, QFileDialog, QProgressDialog)

import tools
import define
from player import Player
from playlist import Playlist
from scanner import Scanner
from config import Config
from server import Server
from database import Database

from gui_library import Library
from gui_control import Control
from gui_control_thread import ControlThread
 




class Init(QWidget):
 

    app = None
    logger = None
    config = None
    database = None
    font = None
    scanner = None
    playlists = []
    server = None
    player = None
    label = None
    layout = None


    def __init__(self, app, config, logger=None):

        super().__init__()    
               
        self.app = app
        self.logger = logger  
        self.config = config

        # font

        font = QFont()
        font.setPixelSize(self.config.fontSize)

        # label

        icon = QLabel()
        image = QPixmap(define.ICONFILE)
        icon.setPixmap(image)
        icon.setAlignment(Qt.AlignCenter)
        self.label = QLabel()       

        # main
        
        self.layout = QVBoxLayout()        
        self.layout.addWidget(icon)
        self.layout.addWidget(self.label)             
        self.setLayout(self.layout)   

        # show
        self.setWindowFlags(Qt.CustomizeWindowHint)  
        self.setFixedHeight(image.size().height() + 50)
        self.setFixedWidth(600)
        self.show()                     

        # database

        self.database = Database(logger=self)
        try:
            self.database.open(define.DBFILE)
        except:
            tools.error('could not open database ', self.logger)    

        ## scan

        self.scanner = Scanner(self.config, self.database, logger=self)        
        try:
            self.playlists = self.scanner.scan() 
        except:
            tools.error('could not scan playlists', self.logger)        
      
        # mpd

        if self.config.startMpd:
            if not tools.islinux():
                self.server = Server(logger=self)
                self.server.start(define.MPDFILE, conf=os.path.realpath(self.config.confPath)) 

        # player    

        self.player = Player(self.database, logger=self)
        if self.player.connect():
            self.player.update()
        else:
            tools.error('could not connect player', self.logger)      

    
        # redirect logging

        self.server.logger = self.logger
        self.player.logger = self.logger        
        

    def info(self, message : str):

        self.label.setText(message)
        self.update()

        tools.info(message, self.logger)
        self.app.processEvents()


    def exception(self, message : str):

        self.label.setText(message)
        self.update()

        tools.error(message, self.logger)
        self.app.processEvents()
            
 
if __name__ == '__main__':

    # logger

    logger = logging.getLogger('pyabp')
    logFileHandler = logging.FileHandler(define.LOGFILE)
    logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logFileHandler.setFormatter(logFormatter)
    logger.addHandler(logFileHandler) 
    logger.setLevel(logging.DEBUG)

    # config

    config = tools.readConfig(define.CONFFILE,logger=logger) 

    # run

    app = QApplication(sys.argv)
    init = Init(app, config, logger=logger)
    sys.exit(app.exec_())
