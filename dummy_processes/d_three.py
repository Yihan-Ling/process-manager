from time import sleep
from process_manager.log import logger
from process_manager.util import auto_default_logging
import logging.handlers

_log = logger(__file__)

handler = logging.handlers.SocketHandler('localhost', 9020)
handler.setLevel(logging.DEBUG)
_log.addHandler(handler)

var = 0
while True:
    _log.info("d_three running")
    var+=1
    sleep(1)
    
print("d_three exits")
    