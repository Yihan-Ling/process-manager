import igmr_robotics_toolkit.comms.auto_init  
import logging
from time import time
from igmr_robotics_toolkit.comms.params import ParameterClient
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic
from process_manager.types import LogMessage

class DDSLogHandler(logging.Handler):
    def __init__(self, topic_name="process_manager/logs"):
        super().__init__()
        self.params = ParameterClient()
        self.dp = self.params.participant
        self.pub = Publisher(self.dp)
        self.log_writer = DataWriter(self.pub, Topic(self.dp, topic_name, LogMessage))

    def emit(self, record: logging.LogRecord):
        try:
            msg = LogMessage(
                name=record.name,
                levelno=record.levelno,
                message=record.getMessage(),
                timestamp=time()
            )
            self.log_writer.write(msg)
        except Exception:
            self.handleError(record)
