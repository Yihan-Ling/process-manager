import igmr_robotics_toolkit.comms.auto_init
from typing import Iterable, Mapping, Tuple
import sys
import subprocess
from time import time, sleep
from threading import Thread
import logging.handlers

from process_manager.log import logger
from process_manager.util import auto_default_logging

from cyclonedds.qos import Qos, Policy
from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic

from igmr_robotics_toolkit.comms.history import SubscribedStateBuffer
from igmr_robotics_toolkit.comms.params import ParameterClient, StateClient
from igmr_robotics_toolkit.comms.history import OutOfWindowException

from process_manager.types import ProcessState

from process_manager.log.dds_handler import DDSLogHandler

_log = logger(__file__)


dds_handler = DDSLogHandler()
dds_handler.setLevel(logging.DEBUG)
_log.addHandler(dds_handler)
class Node():
    def __init__(self, module_name: str, popen: subprocess.Popen, cmd_args: list[str], pc: ParameterClient):
        self.module_name = module_name.rsplit(".", 1)[-1]
        self.name = pc.get(f"process_manager/{self.module_name}")
        self.popen = popen
        self.logs = []
        self.recent_severities: list[str] = []
        self.cmd_args = cmd_args 
        self.start_time = time()
        self.end_time = None
        self.launched_times = 0
        self.relaunched = False
        self.log_severity = "DEBUG" # Default to start at DEBUG
        self.params = pc
        self.awaiting_state_since: float | None = time()
        self.forced_stop = False
        with self.params:
            dp = self.params.participant
            self.state_reader = SubscribedStateBuffer(self.params.get(f'process_manager/{self.module_name}'), ProcessState, domain_participant=dp)
        
    
    def is_alive(self) -> bool:
        try:
            _, state = self.state_reader.latest
            if state.alive:
                self.awaiting_state_since = None
            return state.alive
        except OutOfWindowException:
            return False

    def get_uptime(self) -> float:
        # if self.end_time:
        #     return self.end_time - self.start_time
        # elif self.is_alive():
        #     return time() - self.start_time
        # else:
        #     self.end_time = time()
        #     return self.end_time - self.start_time
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
        self.stopAll = False
        try:
            self.params = ParameterClient()
        except ParameterClient.InitializationTimeout:
            print('parameter initialization timed out (is the parameter server running?)')
            raise SystemExit(1)
        
        # with params:
        #     dp = params.participant

        #     sub = Subscriber(dp)
        #     # only operate on the most recent input
        #     qos = Qos(Policy.History.KeepLast(1))
        #     # pub = Publisher(dp)
        #     self.state_reader = SubscribedStateBuffer(params.get('process_manager/d_one'), ProcessState, domain_participant=dp)
        
        
    def launch(self, module: str, *cmd_args: Iterable[object], **cmd_kwargs: Mapping[str, object]) -> subprocess.Popen:
        arg = [sys.executable, '-u', '-m', module] + \
            [str(o) for o in cmd_args] + \
            [f"--{k.replace('_', '-')}={v}" for (k, v) in cmd_kwargs.items()]
        node = Node(module_name=module, 
            popen=
            subprocess.Popen(
                arg,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            ),
            cmd_args=arg,
            pc = self.params 
        )
        self.processes.append(node)
        
        # Thread(target=self._read_node_output, args=(node,), daemon=True).start()


    def relaunch_node(self, failed_node: Node):
        _log.info(f"Relaunching node: {failed_node.name}")
        failed_node.start_time = time()
        failed_node.awaiting_state_since = time()
        new_popen = subprocess.Popen(
            failed_node.cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        failed_node.popen = new_popen
        failed_node.launched_times += 1
        # failed_node.relaunched = True
        # If restart as a new node
        # new_node = Node(module_name=f'{failed_node.module_name}', popen=new_popen, cmd_args=failed_node.cmd_args, pc=failed_node.params)
        # new_node.launched_times = failed_node.launched_times + 1
        # # self.processes.remove(failed_node)
        # self.processes.append(new_node)
        # Thread(target=self._read_node_output, args=(new_node,), daemon=True).start()

    def _query_nodes(self) -> tuple[list[Node], list[Node]]:
        active, failed = [], []
        for n in self.processes:
            if n.is_alive():
                n.relaunched = False
                active.append(n)
            # elif time() - n.start_time > 2:
            elif n.popen.poll() is not None:
                failed.append(n)
                
        return active, failed

    # def _read_node_output(self, node: Node):
    #     for line in node.popen.stdout:
    #         line = line.strip()
    #         node.logs.append(line)
    #         self.terminal_prints.append(line)
    #         if len(node.logs) > 100:
    #             node.logs.pop(0)
    #         if len(self.terminal_prints) > 100:
    #             self.terminal_prints.pop(0)
    
    def watch(self, period=1):
        
        try:
            while True:
                if self.stopAll:
                    break
                sleep(period)
                (active, failed) = self._query_nodes()
                # TODO: chnage this maybe
                if len(failed)>=1:
                    for failed_node in failed:
                        _log.warning(f'Node {failed_node.name} has failed')
                        if (not failed_node.relaunched) and (not failed_node.forced_stop):
                            self.relaunch_node(failed_node)
                            failed_node.relaunced = True
                        
                        # failed_node.relaunched = False
                    # break

        except KeyboardInterrupt:
            _log.warning('initiating shutdown due to interrupt')

        # for n in self.active:
        #     if platform.system() == 'Windows':
        #         n.send_signal(signal.CTRL_C_EVENT)
        #     else:
        #         n.send_signal(signal.SIGINT)

        # for n in self.processes:
        #     try:
        #         n.popen.wait()
        #     except KeyboardInterrupt:
        #         pass

        # for n in self.failed:
        #     _log.critical(f'node {n.args} failed')
            
    def stop_all(self):
        self.stopAll = True 
        for node in self.processes:
            if node.is_alive():
                try:
                    node.popen.terminate()
                    node.popen.wait(timeout=5)
                except Exception as e:
                    _log.critical(f"Failed to terminate {node.name}: {e}")
