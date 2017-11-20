import sys
import logging
import define
import tools

from PyQt5.QtWidgets import QApplication

from config import Config
from gui_main import Main
from gui_init import Init

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
init.hide()  
main = Main(app, config, init.server, init.player, init.playlists, logger=logger)    
sys.exit(app.exec_())
