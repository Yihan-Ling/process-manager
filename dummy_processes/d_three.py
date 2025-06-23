from time import sleep
from process_manager.log import logger
from process_manager.util import auto_default_logging

_log = logger(__file__)
var = 0
while True:
    _log.info("d_three running")
    var+=1
    sleep(1)
    
print("d_three exits")
    