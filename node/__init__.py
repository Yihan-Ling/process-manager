import platform
from typing import Iterable, Mapping, Tuple
import sys
import subprocess
import signal
from time import sleep

from process_manager.log import logger
_log = logger
# import igmr_robotics_toolkit
# _log = igmr_robotics_toolkit.logger(__file__)

def launch(module: str, *cmd_args: Iterable[object], **cmd_kwargs: Mapping[str, object]) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, '-m', module] +
        [str(o) for o in cmd_args] +
        [f"--{k.replace('_', '-')}={v}" for (k, v) in cmd_kwargs.items()]
    )

def _query_nodes(nodes: Iterable[subprocess.Popen]) -> Tuple[Iterable[subprocess.Popen], Iterable[subprocess.Popen]]:
    active = []
    failed = []

    for n in nodes:
        if n.poll() is None:
            active.append(n)
        else:
            failed.append(n)

    return (active, failed)

def watch(*nodes: Iterable[subprocess.Popen], period=2):
    
    try:
        while True:
            sleep(period)

            (active, failed) = _query_nodes(nodes)
            if failed:
                _log.warning('initiating shutdown due to node failure')
                break

    except KeyboardInterrupt:
        _log.warning('initiating shutdown due to interrupt')

    for n in active:
        if platform.system() == 'Windows':
            n.send_signal(signal.CTRL_C_EVENT)
        else:
            n.send_signal(signal.SIGINT)

    for n in nodes:
        try:
            n.wait()
        except KeyboardInterrupt:
            pass

    for n in failed:
        _log.critical(f'node {n.args} failed')
