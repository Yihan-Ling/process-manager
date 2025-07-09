from cyclonedds.domain import DomainParticipant
from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.topic import Topic
from cyclonedds.idl import IdlStruct
from dataclasses import dataclass
from cyclonedds.idl.types import sequence

import igmr_robotics_toolkit.comms.auto_init


# from cyclonedds.idl import String
@dataclass
class Hello(IdlStruct):
    msg: str
    
@dataclass
class ParameterValue(IdlStruct):
    kp:    sequence[str]
    value: str

# Initialize the DDS participant, subscriber, and reader
dp = DomainParticipant(0)
sub = Subscriber(dp)
topic = Topic(dp, "hello_topic", Hello)
reader = DataReader(sub, topic)

init_reader = DataReader(sub, Topic(dp, '_params/init', ParameterValue))

print("Subscriber is waiting for messages...")

while True:
    # Take the message from the reader
    for sample in init_reader.take():
        print(f"Received message: {sample.alive}")
