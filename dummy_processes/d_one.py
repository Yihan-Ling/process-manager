from time import sleep
from process_manager.log import logger
from process_manager.util import auto_default_logging
import logging.handlers


from cyclonedds.qos import Qos, Policy
from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic
from igmr_robotics_toolkit.comms import auto_init

from igmr_robotics_toolkit.comms.history import SubscribedStateBuffer
from igmr_robotics_toolkit.comms.params import ParameterClient, StateClient

from process_manager.types import ProcessState

_log = logger(__file__)

handler = logging.handlers.SocketHandler('localhost', 9020)
handler.setLevel(logging.DEBUG)
_log.addHandler(handler)


try:
    params = ParameterClient()
    # sc = StateClient()
except ParameterClient.InitializationTimeout:
    _log.critical('parameter initialization timed out (is the parameter server running?)')
    raise SystemExit(1)

with params:
    dp = params.participant

    sub = Subscriber(dp)
    # only operate on the most recent input
    qos = Qos(Policy.History.KeepLast(1))
    pub = Publisher(dp)
    state_writer = DataWriter(pub, Topic(dp, params.get('process_manager/d_one'), ProcessState))

var = 0
while  var<15:
    _log.info(var)
    state_writer.write(ProcessState(
        True
    ))
    var += 1
    sleep(1)
state_writer.write(ProcessState(
    False
))
_log.critical("d_one exits")
