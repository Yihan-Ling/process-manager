from threading import Thread
from process_manager.node import Watcher, Node
from process_manager.ui import Process_Manager_App
from process_manager.log.logger import logger

def start_processes(watcher):
    watcher.launch('process_manager.dummy_processes.d_one')
    watcher.launch('process_manager.dummy_processes.d_two')
    watcher.launch('process_manager.dummy_processes.d_three')

def run_watch():
    watcher.watch(
        # TODO: make period adjustable in UI
        period=1
    )
    
def _read_output(node: Node):
    for line in node.popen.stdout:
        node.logs.append(line.strip())



if __name__ == "__main__":
    watcher = Watcher()
    logger.info("Starting the process manager...")
    start_processes(watcher)
    
    watch_thread = Thread(target=run_watch)
    watch_thread.daemon = True  # Allow this thread to exit when the main program exits
    watch_thread.start()
    
    for node in watcher.processes:
        Thread(target=_read_output, args=(node,), daemon=True).start()
    
    # When launching:
    # Thread(target=_read_output, args=(node,), daemon=True).start()
    
    # Start the UI thread (Textual app)
    app = Process_Manager_App(watcher = watcher)
    app.run()
