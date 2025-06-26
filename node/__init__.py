import platform
from typing import Iterable, Mapping, Tuple
import sys
import subprocess
import signal
from time import time, sleep
# from process_manager.log.logger import logger
from threading import Thread
# import igmr_robotics_toolkit
# _log = igmr_robotics_toolkit.logger(__file__)

from process_manager.log import logger
from process_manager.util import auto_default_logging

_log = logger(__file__)


class Node():
    def __init__(self, name: str, popen: subprocess.Popen, cmd_args: list[str]):
        self.name = name
        self.popen = popen
        self.logs = []
        self.cmd_args = cmd_args 
        self.start_time = time()
        self.end_time = None
        self.launched_times = 0
        self.relaunched = False
    
    def is_alive(self) -> bool:
        return self.popen.poll() is None
    
    def get_uptime(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        elif self.is_alive():
            return time() - self.start_time
        else:
            self.end_time = time()
            return self.end_time - self.start_time

class Watcher():
    def __init__(self):
        self.active = []
        self.failed = []
        self.processes: list[Node] = []
        self.logs = []
        self.stopAll = False
        
    def launch(self, module: str, *cmd_args: Iterable[object], **cmd_kwargs: Mapping[str, object]) -> subprocess.Popen:
        arg = [sys.executable, '-u', '-m', module] + \
            [str(o) for o in cmd_args] + \
            [f"--{k.replace('_', '-')}={v}" for (k, v) in cmd_kwargs.items()]
        node = Node(name=module, 
            popen=
            subprocess.Popen(
                arg,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            ),
            cmd_args=arg 
        )
        self.processes.append(node)
        
        # Thread(target=self._read_node_output, args=(node,), daemon=True).start()


    def relaunch_node(self, failed_node: Node) -> Node:
        _log.info(f"Relaunching node: {failed_node.name}")
        new_popen = subprocess.Popen(
            failed_node.cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        new_node = Node(name=f'{failed_node.name}', popen=new_popen, cmd_args=failed_node.cmd_args)
        new_node.launched_times = failed_node.launched_times + 1
        # self.processes.remove(failed_node)
        self.processes.append(new_node)
        # Thread(target=self._read_node_output, args=(new_node,), daemon=True).start()

    def _query_nodes(self) -> Tuple[Iterable[subprocess.Popen], Iterable[subprocess.Popen]]:
        active = []
        failed = []
        for n in self.processes:
            if n.is_alive():
                active.append(n)
            elif not n.relaunched:
                failed.append(n)

        return (active, failed)

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
                (self.active, self.failed) = self._query_nodes()
                # TODO: chnage this maybe
                if len(self.failed)>=1:
                    for failed_node in self.failed:
                        _log.warning(f'Node {failed_node.name} has failed')
                        failed_node.relaunched = True
                        self.relaunch_node(failed_node)

                    # break

        except KeyboardInterrupt:
            _log.warning('initiating shutdown due to interrupt')

        for n in self.active:
            if platform.system() == 'Windows':
                n.send_signal(signal.CTRL_C_EVENT)
            else:
                n.send_signal(signal.SIGINT)

        for n in self.processes:
            try:
                n.popen.wait()
            except KeyboardInterrupt:
                pass

        for n in self.failed:
            _log.critical(f'node {n.args} failed')
            
    def stop_all(self):
        print("1")
        self.stopAll = True 
        for node in self.processes:
            if node.is_alive():
                try:
                    node.popen.terminate()
                    node.popen.wait(timeout=5)
                except Exception as e:
                    print(f"Failed to terminate {node.name}: {e}")
