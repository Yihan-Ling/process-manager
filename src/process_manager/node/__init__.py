from __future__ import annotations
import igmr_robotics_toolkit.comms.auto_init
from typing import Iterable, Mapping
import sys
import subprocess
from time import time, sleep

from process_manager.log import logger
from process_manager.util import auto_default_logging

from cyclonedds.qos import Qos, Policy
from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic

from igmr_robotics_toolkit.comms.params import ParameterClient

from process_manager.types import Heartbeat

from pathlib import Path

_log = logger(__file__)

class Node():
    def __init__(self, name: str, module_name: str, popen: subprocess.Popen, cmd_args: list[str], watcher: Watcher):
        self.module_name = module_name
        self.name = name
        self.popen = popen
        self.logs = []
        self.recent_severities: list[str] = []
        self.cmd_args = cmd_args 
        self.start_time = time()
        self.end_time = None
        self.launched_times = 0
        self.log_severity = "DEBUG" # Default to start at DEBUG
        self.forced_stop = False
        self.watcher = watcher
        self.time_of_last_warning = None
    
    def is_alive(self) -> bool:
        last_beat = self.watcher.last_heartbeats.get(self.name)
        if last_beat is None:
            _log.debug(f"No heartbeat ever received from {self.name}")
            return False
        if time() - last_beat >= 2.0:
            return False
        return True

    def get_uptime(self) -> float:
        if not self.is_alive():
            return 0.0
        return time()-self.start_time
        
    def update_severity(self, level: str):
        severity_order = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.recent_severities.append(level)
        if len(self.recent_severities) > 50:
            self.recent_severities.pop(0)
            
        max_index = max(severity_order.index(lvl) for lvl in self.recent_severities)
        self.log_severity = severity_order[max_index]

            
    def get_severity_color(self) -> str:
        return {
            "DEBUG": "white",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "orange",
            "CRITICAL": "red",
        }.get(self.log_severity, "gray")

class Watcher():
    def __init__(self):
        self.active = []
        self.failed = []
        self.processes: list[Node] = []
        self.logs = []
        self.main_logs = []
        self.last_heartbeats: dict[str, float] = {}
        self.stopAll = False
        self.registered_names = []
        try:
            self.params = ParameterClient()
        except ParameterClient.InitializationTimeout:
            print('parameter initialization timed out (is the parameter server running?)')
            raise SystemExit(1)
        
        with self.params:
            dp = self.params.participant
            sub = Subscriber(dp)
            topic = Topic(dp, "heart_beats", Heartbeat)
            self.heartbeat_reader = DataReader(sub, topic, qos=Qos(Policy.History.KeepLast(100)))
        
        
    def launch(self, name: str, module: str, *cmd_args: Iterable[object], **cmd_kwargs: Mapping[str, object]) -> subprocess.Popen:
        arg = [sys.executable, '-u', '-m', module] + \
            [str(o) for o in cmd_args] + \
            [f"--{k.replace('_', '-')}={v}" for (k, v) in cmd_kwargs.items()]
        node = Node(
            name = name,
            module_name=module, 
            popen=
            subprocess.Popen(
                arg,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            ),
            cmd_args=arg,
            watcher=self
        )
        self.processes.append(node)
        self.registered_names.append(node.name)


    def relaunch_node(self, failed_node: Node):
        if self.stopAll: 
            return
        _log.info(f"Relaunching node: {failed_node.name}")
        failed_node.start_time = time()
        new_popen = subprocess.Popen(
            failed_node.cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        failed_node.popen = new_popen
        failed_node.launched_times += 1
        

    def _query_nodes(self) -> tuple[list[Node], list[Node]]:
        active, failed = [], []
        for n in self.processes:
            if n.is_alive():
                active.append(n)
            else:
                failed.append(n)
                
        return active, failed
    
    
    def watch(self, period=1):
        
        try:
            while True:
                if self.stopAll:
                    break
                sleep(period)
                
                (active, failed) = self._query_nodes()
                if len(failed)>=1:
                    for failed_node in failed:
                        _log.warning(f'Node {failed_node.name} has failed')
                        if (not failed_node.forced_stop) and failed_node.popen.poll() is not None:
                            self.relaunch_node(failed_node)

        except KeyboardInterrupt:
            _log.warning('initiating shutdown due to interrupt')

            
    def stop_all(self):
        _log.warning("Shutting down...")
        self.stopAll = True 
        for node in self.processes:
            try:
                node.popen.terminate()
                node.popen.wait(timeout=5)
            except Exception as e:
                _log.critical(f"Failed to terminate {node.name}: {e}")
                    
    def launch_script(self, path: Path, name: str):
        proc = subprocess.Popen(
            [sys.executable, "-u", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        node = Node(
            name=name,
            module_name=str(path),  
            popen=proc,
            cmd_args=[str(path)],
            watcher=self
        )
        self.processes.append(node)
        self.registered_names.append(name)
    