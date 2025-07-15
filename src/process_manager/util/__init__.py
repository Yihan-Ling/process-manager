import igmr_robotics_toolkit.comms.auto_init    # Has to import before CycloneDDS
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic

from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.qos import Qos, Policy
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic

from igmr_robotics_toolkit.comms.params import ParameterClient, StateClient

from process_manager.types import Heartbeat
import time
from logging import Logger

def default_logging():
    import logging, coloredlogs
    coloredlogs.DEFAULT_LOG_FORMAT = '%(asctime)s.%(msecs)03d %(filename)15s:%(lineno)03d %(levelname)7s: %(message)s'
    coloredlogs.install(level=logging.DEBUG, logger=logging.getLogger('__main__'))
    coloredlogs.install(level=logging.DEBUG, logger=logging.getLogger('ui'))
    coloredlogs.install(level=logging.DEBUG, logger=logging.getLogger('dummy_processes'))
    coloredlogs.install(level=logging.DEBUG, logger=logging.getLogger('node'))

def write_heartbeat(writer: DataWriter, module: str = None):
    params = ParameterClient()
    with params:
        resolved_name = params.get(f"processes/{module}")

    writer.write(Heartbeat(name=resolved_name, timestamp=time.time()))
    
def create_writer(_log:Logger) -> DataWriter:
    try:
        _log.warning("loading parameters")
        params = ParameterClient()
        sc = StateClient()
    except ParameterClient.InitializationTimeout:
        _log.error('parameter initialization timed out (is the parameter server running?)')
        raise SystemExit(1)

    with params:
        dp = params.participant
        pub = Publisher(dp)
        state_writer = DataWriter(pub, Topic(dp, "heart_beats", Heartbeat))
    return state_writer 