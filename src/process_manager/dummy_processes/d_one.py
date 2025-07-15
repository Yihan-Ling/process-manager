from time import sleep, time
from process_manager.log import logger
from process_manager.util import auto_default_logging
import igmr_robotics_toolkit.comms.auto_init    # Has to import before CycloneDDS

from process_manager.util import write_heartbeat, create_writer

_log = logger(__file__)

state_writer = create_writer(_log)

var = 0
while  var<15:
    _log.info(var)
    print(var)
    write_heartbeat(writer=state_writer, module=__spec__.name)
    var += 1
    sleep(1)
_log.critical("d_one exits")
