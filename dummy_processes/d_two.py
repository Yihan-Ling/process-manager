from time import sleep
from random import random
from process_manager.log import logger
from process_manager.util import auto_default_logging

_log = logger(__file__)

while random()>0.1:
    _log.info("d_two run")
    sleep(2)
_log.warning("d_two exit")
