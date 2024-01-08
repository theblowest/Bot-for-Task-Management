import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('bot.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)


logging.debug(u'This is a debug message')
logging.info(u'This is an info message')
logging.warning(u'This is a warning')
logging.error(u'This is an error message')
logging.critical(u'FATAL!!!')