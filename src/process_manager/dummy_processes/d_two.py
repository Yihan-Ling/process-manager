from time import sleep, time
from process_manager.log import logger
from process_manager.util import auto_default_logging
import igmr_robotics_toolkit.comms.auto_init    # Has to import before CycloneDDS

from process_manager.util import write_heartbeat, create_writer

import random

_log = logger(__file__)

state_writer = create_writer(_log)

while random.random()>0.1:
    _log.info("d_two run")
    write_heartbeat(writer=state_writer, module=__spec__.name)
    sleep(2)

_log.warning("d_two exit")
