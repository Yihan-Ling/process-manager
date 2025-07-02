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

from process_manager.types import ProcessState
import random

_log = logger(__file__)

handler = logging.handlers.SocketHandler('localhost', 9020)
handler.setLevel(logging.DEBUG)
_log.addHandler(handler)

try:
    _log.info("loading parameters")
    params = ParameterClient()
    sc = StateClient()
except ParameterClient.InitializationTimeout:
    _log.error('parameter initialization timed out (is the parameter server running?)')
    raise SystemExit(1)

with params:
    dp = params.participant

    sub = Subscriber(dp)
    # only operate on the most recent input
    qos = Qos(Policy.History.KeepLast(1))
    pub = Publisher(dp)
    state_writer = DataWriter(pub, Topic(dp, params.get('process_manager.dummy_processes.d_two'), ProcessState))

while random()>0.1:
    _log.info("d_two run")
    state_writer.write(ProcessState(
        alive = True,
        timestamp = time()
    ))
    sleep(2)
state_writer.write(ProcessState(
    alive = False,
    timestamp = time()
))
_log.warning("d_two exit")
