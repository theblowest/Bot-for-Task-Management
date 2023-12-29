import logging

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG, filename=u'bot.log')

logging.debug(u'This is a debug message')
logging.info(u'This is an info message')
logging.warning(u'This is a warning')
logging.error(u'This is an error message')
logging.critical(u'FATAL!!!')