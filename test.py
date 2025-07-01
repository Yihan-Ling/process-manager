from time import sleep
from cyclonedds.qos import Qos, Policy
from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic
from igmr_robotics_toolkit.comms import auto_init

from igmr_robotics_toolkit.comms.history import SubscribedStateBuffer
from igmr_robotics_toolkit.comms.params import ParameterClient, StateClient

from process_manager.types import ProcessState

try:
    params = ParameterClient()
    # sc = StateClient()
except ParameterClient.InitializationTimeout:
    print('parameter initialization timed out (is the parameter server running?)')
    raise SystemExit(1)

with params:
    dp = params.participant

    sub = Subscriber(dp)
    # only operate on the most recent input
    qos = Qos(Policy.History.KeepLast(1))
    pub = Publisher(dp)
    state_reader = SubscribedStateBuffer(params.get('process_manager/d_one'), ProcessState, domain_participant=dp)

while True:
    state = state_reader.latest()
    print(state)
    sleep(1)