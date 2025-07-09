from threading import Thread
from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.qos import Qos, Policy
from cyclonedds.topic import Topic
from igmr_robotics_toolkit.comms.params import ParameterClient
from process_manager.types import LogMessage


def start_dds_log_listener(watcher):
    try:
        params = ParameterClient()
        # sc = StateClient()
    except ParameterClient.InitializationTimeout:
        print('parameter initialization timed out (is the parameter server running?)')
        raise SystemExit(1)
    with params:
        dp = params.participant
        sub = Subscriber(dp)
        topic = Topic(dp, "process_manager/logs", LogMessage)
        reader = DataReader(sub, topic, qos=Qos(Policy.History.KeepLast(100)))

    def listen():
        while True:
            msgs = reader.take()
            for msg in msgs:
                formatted = f"{msg.name}  [{msg.levelname}]: {msg.message}"

                # Store in global log buffer
                watcher.logs.append(formatted)
                if len(watcher.logs) > 1000:
                    watcher.logs.pop(0)

                # Try to route to the correct node
                for node in watcher.processes:
                    if node.module_name in msg.name:
                        node.logs.append(formatted)
                        if len(node.logs) > 1000:
                            node.logs.pop(0)
                        node.update_severity(msg.levelname)
                        break
                else:
                    watcher.main_logs.append(formatted)

    Thread(target=listen, daemon=True).start()