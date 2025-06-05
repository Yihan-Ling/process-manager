import platform
from typing import Iterable, Mapping, Tuple
import sys
import subprocess
import signal
from time import time, sleep
from process_manager.log import logger
_log = logger
# import igmr_robotics_toolkit
# _log = igmr_robotics_toolkit.logger(__file__)


class Node():
    def __init__(self, name: str, popen: subprocess.Popen):
        self.name = name
        self.popen = popen
        self.start_time = time()
        self.last_output = ""
        self.active = True
    
    def is_alive(self) -> bool:
        return self.active

class Watcher():
    def __init__(self):
        self.active = []
        self.failed = []
        self.processes: list[Node] = []
        
    def launch(self, module: str, *cmd_args: Iterable[object], **cmd_kwargs: Mapping[str, object]) -> subprocess.Popen:
        self.processes.append(
            Node(name=module, 
                         popen=
                subprocess.Popen(
                    [sys.executable, '-m', module] +
                    [str(o) for o in cmd_args] +
                    [f"--{k.replace('_', '-')}={v}" for (k, v) in cmd_kwargs.items()]
                )   
            )
        )

    def _query_nodes(self) -> Tuple[Iterable[subprocess.Popen], Iterable[subprocess.Popen]]:
        active = []
        failed = []
        for n in self.processes:
            if n.popen.poll() is None:
                n.active = True
                active.append(n.popen)
            else:
                n.active = False
                failed.append(n.popen)

        return (active, failed)

    def watch(self, period=2):
        
        try:
            while True:
                sleep(period)

                (self.active, self.failed) = self._query_nodes()
                if self.failed:
                    _log.warning('initiating shutdown due to node failure')
                    break

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
