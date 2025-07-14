from cyclonedds.domain import DomainParticipant
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic
from cyclonedds.idl import IdlStruct
# from cyclonedds.idl import String
import time
from dataclasses import dataclass
# from cyclonedds.idl import String
@dataclass
class Hello(IdlStruct):
    msg: str

dp = DomainParticipant()
pub = Publisher(dp)
topic = Topic(dp, "hello_topic", Hello)
writer = DataWriter(pub, topic)

print("Publisher is sending...")
while True:
    writer.write(Hello("Hello DDS"))
    time.sleep(1)
