from time import sleep
import igmr_robotics_toolkit.comms.auto_init

from cyclonedds.qos import Qos, Policy
from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic

from igmr_robotics_toolkit.comms.history import SubscribedStateBuffer
from igmr_robotics_toolkit.comms.params import ParameterClient, StateClient
from igmr_robotics_toolkit.comms.history import OutOfWindowException

from process_manager.types import ProcessState, LogMessage


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

    # reader = SubscribedStateBuffer("process_manager/logs", LogMessage, domain_participant=dp)
    topic = Topic(dp, "process_manager/logs", LogMessage)
    reader = DataReader(sub, topic, qos=Qos(Policy.History.KeepLast(100)))

while True:
    samples = reader.take() 
    if not samples:
        print("No messages.")
    for sample in samples:
        msg = sample
        print(f"[{msg.levelname}] {msg.name}: {msg.message}")

    sleep(1)