import logging
from datetime import datetime
import os

def setup_logger(log_file: str='bank_app.log'):
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt=date_format, handlers=[logging.FileHandler(log_file, encoding='utf-8'), logging.StreamHandler()])
    logger = logging.getLogger('bank_app')
    logger.info('=' * 60)
    logger.info('Application started')
    logger.info('=' * 60)
    return logger
