import os
import logging
from logging.handlers import RotatingFileHandler

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIRECTORY_NAME = 'logs'
LOG_FILE_NAME = 'app.log'
LOG_FILE_PATH = os.path.join(BASE_DIR,LOG_DIRECTORY_NAME)
os.makedirs(LOG_FILE_PATH, exist_ok=True)
LOG_FILE = os.path.join(LOG_FILE_PATH,LOG_FILE_NAME)

filehandler = RotatingFileHandler(
    filename=LOG_FILE,
    maxBytes=1024*1024*5,
    backupCount=5,
    encoding='utf-8'
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[filehandler]
)