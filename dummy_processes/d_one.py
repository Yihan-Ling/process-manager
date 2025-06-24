from time import sleep
from process_manager.log import logger
from process_manager.util import auto_default_logging
import logging.handlers

_log = logger(__file__)

handler = logging.handlers.SocketHandler('localhost', 9020)
handler.setLevel(logging.DEBUG)
_log.addHandler(handler)

var = 0
while  var<15:
    _log.info(var)
    var += 1
    sleep(1)
_log.warning("d_one exits")
