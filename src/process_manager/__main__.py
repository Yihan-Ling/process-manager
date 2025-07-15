from time import sleep, time
import igmr_robotics_toolkit.comms.auto_init
from threading import Thread
from process_manager.node import Watcher
from process_manager.ui import Process_Manager_App
from process_manager.log import logger
from process_manager.util import auto_default_logging
from process_manager.log.server import start_log_server
from process_manager.log.dds_handler import DDSLogHandler
import logging
from process_manager.log.log_listener import start_dds_log_listener

from cyclonedds.qos import Qos, Policy
from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic

from igmr_robotics_toolkit.comms.history import SubscribedStateBuffer
from igmr_robotics_toolkit.comms.params import ParameterClient, StateClient
from igmr_robotics_toolkit.comms.history import OutOfWindowException

from process_manager.types import LogMessage, Heartbeat

import sys
from pathlib import Path
import yaml
import subprocess
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

_log = logger(__file__)

# dds_handler = DDSLogHandler()
# dds_handler.setLevel(logging.DEBUG)
# _log.addHandler(dds_handler)


def start_processes(watcher: Watcher):
    # Get project root and config path
    project_root = Path(__file__).resolve().parents[2]
    config_path = Path(__file__).parent / "config.yaml"

    if not config_path.exists():
        _log.error(f"Config file not found at {config_path}")
        return

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    processes = config.get("processes", {})
    if not processes:
        _log.warning("No processes defined in config.yaml")
        return

    for module, name in processes.items():
        _log.info(f"Launching module: {name} ({module})")
        watcher.launch(name=name, module=module)

def run_watch(watcher: Watcher):
    watcher.watch(
        # TODO: make period adjustable in UI
        period=1
    )
    
def track_heartbeats(watcher: Watcher):
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
                # print("No messages.")
                continue
            msg = sample
            watcher.last_heartbeats[msg.name] = msg.timestamp    
    
def main():
    watcher = Watcher()
    _log.info("Starting the process manager...")
    
    # log_server = start_log_server(watcher)
    start_dds_log_listener(watcher)
    
    watch_thread = Thread(target=run_watch, args=(watcher,))
    watch_thread.daemon = True 
    watch_thread.start()
    
    hb_thread = Thread(target=track_heartbeats, args=(watcher,))
    hb_thread.daemon = True 
    hb_thread.start()
    
    start_processes(watcher)
    
    app = Process_Manager_App(watcher=watcher)
    # app.log_server = log_server 
    app.run()

if __name__ == "__main__":
    main()