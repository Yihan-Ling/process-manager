from threading import Thread
from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.qos import Qos, Policy
from cyclonedds.topic import Topic
from igmr_robotics_toolkit.comms.params import ParameterClient
from process_manager.types import LogMessage


def start_dds_log_listener(watcher):
    """
    Start a background thread to listen for LogMessage DDS messages
    and route them to the appropriate watcher and nodes.
    """
    params = ParameterClient()
    dp = params.participant
    sub = Subscriber(dp)
    topic = Topic(dp, "process_manager/logs", LogMessage)
    reader = DataReader(sub, topic, qos=Qos(Policy.History.KeepLast(10)))

    def listen():
        while True:
            sample = reader.read()
            for msg in sample:
                record = msg[0]
                formatted = f"{record.name} {record.levelname}: {record.message}"

                # Store in global log buffer
                watcher.logs.append(formatted)
                if len(watcher.logs) > 1000:
                    watcher.logs.pop(0)

                # Try to route to the correct node
                for node in watcher.processes:
                    if record.name in node.module_name or node.module_name in record.name:
                        node.logs.append(formatted)
                        if len(node.logs) > 1000:
                            node.logs.pop(0)
                        node.update_severity(record.levelname)
                        break
                else:
                    watcher.main_logs.append(formatted)

    Thread(target=listen, daemon=True).start()