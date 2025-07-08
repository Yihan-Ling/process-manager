import logging
from time import time
from igmr_robotics_toolkit.comms.params import ParameterClient
from igmr_robotics_toolkit.comms.auto_init import *
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic
from process_manager.types import LogMessage

class DDSLogHandler(logging.Handler):
    def __init__(self, topic_name="process_manager/logs"):
        super().__init__()
        self.params = ParameterClient()
        self.participant = self.params.participant
        self.publisher = Publisher(self.participant)
        self.topic = Topic(self.participant, topic_name, LogMessage)
        self.writer = DataWriter(self.publisher, self.topic)

    def emit(self, record: logging.LogRecord):
        try:
            msg = LogMessage(
                name=record.name,
                levelname=record.levelname,
                message=record.message,
                timestamp=time()
            )
            self.writer.write(msg)
        except Exception:
            self.handleError(record)
