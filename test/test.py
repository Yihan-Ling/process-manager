from time import sleep, time
import igmr_robotics_toolkit.comms.auto_init

from cyclonedds.qos import Qos, Policy
from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic

from igmr_robotics_toolkit.comms.history import SubscribedStateBuffer
from igmr_robotics_toolkit.comms.params import ParameterClient, StateClient
from igmr_robotics_toolkit.comms.history import OutOfWindowException

from process_manager.types import LogMessage, Heartbeat


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
    topic = Topic(dp, "heart_beats", Heartbeat)
    reader = DataReader(sub, topic, qos=Qos(Policy.History.KeepLast(100)))

while True:
    samples = reader.take() 
    
    for sample in samples:
        if not isinstance(sample, Heartbeat):
            print("No messages.")
            continue
        msg = sample
        print(f"[{msg.name}]: {msg.timestamp}")
        print(time()-msg.timestamp)

    sleep(0.5)