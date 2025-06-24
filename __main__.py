from threading import Thread
from process_manager.node import Watcher, Node
from process_manager.ui import Process_Manager_App
from process_manager.log import logger
from process_manager.util import auto_default_logging
from process_manager.log.server import start_log_server


_log = logger(__file__)


def start_processes(watcher):
    
    watcher.launch('process_manager.dummy_processes.d_one')
    watcher.launch('process_manager.dummy_processes.d_two')
    watcher.launch('process_manager.dummy_processes.d_three')

def run_watch():
    watcher.watch(
        # TODO: make period adjustable in UI
        period=1
    )

if __name__ == "__main__":
    watcher = Watcher()
    _log.info("Starting the process manager...")
    start_processes(watcher)
    log_server = start_log_server(watcher)
    
    watch_thread = Thread(target=run_watch)
    watch_thread.daemon = True  # Allow this thread to exit when the main program exits
    watch_thread.start()
    
    app = Process_Manager_App(watcher=watcher, log_server=log_server)
    app.log_server = log_server  # attach for shutdown access
    app.run()