from time import sleep
from process_manager.log import logger

_log = logger(__file__)
var = 0
while  var<15:
    _log.info(var)
    var += 1
    sleep(1)
_log.warning("d_one exits")
        