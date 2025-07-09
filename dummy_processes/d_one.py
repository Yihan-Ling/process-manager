from time import sleep, time
from process_manager.log import logger
from process_manager.util import auto_default_logging
import logging.handlers
import igmr_robotics_toolkit.comms.auto_init    # Has to import before CycloneDDS

from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.qos import Qos, Policy
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic

from igmr_robotics_toolkit.comms.history import SubscribedStateBuffer
from igmr_robotics_toolkit.comms.params import ParameterClient, StateClient

from process_manager.types import HeartBeat

from process_manager.log.dds_handler import DDSLogHandler

_log = logger(__file__)


dds_handler = DDSLogHandler()
dds_handler.setLevel(logging.DEBUG)
_log.addHandler(dds_handler)


try:
    _log.warning("loading parameters")
    params = ParameterClient()
    sc = StateClient()
except ParameterClient.InitializationTimeout:
    _log.error('parameter initialization timed out (is the parameter server running?)')
    raise SystemExit(1)

with params:
    dp = params.participant
    sub = Subscriber(dp)
    qos = Qos(Policy.History.KeepLast(1))
    pub = Publisher(dp)
    state_writer = DataWriter(pub, Topic(dp, "heart_beats", HeartBeat))

var = 0
while  var<15:
    _log.info(var)
    state_writer.write(HeartBeat(
        name = "d_one",
        timestamp= time()
    ))
    var += 1
    sleep(1)
_log.critical("d_one exits")
