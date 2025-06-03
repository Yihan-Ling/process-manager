from threading import Thread
from process_manager.node import launch, watch
from process_manager.ui import Process_Info, Process_Manager_App
from process_manager.log import logger

def start_processes():
    processes = [
        Process_Info(name="Process 1", popen=launch('dummy_process.d_one')),
        Process_Info(name="Process 2", popen=launch('dummy_process.d_two')),
        Process_Info(name="Process 3", popen=launch('dummy_process.d_three'))
    ]
    return processes

def run_watch(processes):
    watch(
        # TODO: make period adjustable in UI
        *[p.popen for p in processes], period=1
    )

if __name__ == "__main__":
    logger.logger.info("Starting the process manager...")
    processes = start_processes
    
    watch_thread = Thread(target=run_watch)
    watch_thread.daemon = True  # Allow this thread to exit when the main program exits
    watch_thread.start()
    
    # Start the UI thread (Textual app)
    app = Process_Manager_App(processes=processes)
    app.run()
