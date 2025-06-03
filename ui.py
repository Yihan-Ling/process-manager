from textual.app import App, ComposeResult
from textual.widgets import Header
import time

import subprocess

class Process_Info():
    def __init__(self, name: str, popen: subprocess.Popen):
        self.name = name
        self.popen = popen
        self.start_time = time.time()
        self.last_output = ""
        self.status = "Running"

class Process_Manager_App(App):
    def __init__(self, processes: list[Process_Info], **kwargs):
        super().__init__(**kwargs)
        self.processes = processes
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
    
    def on_mount(self) -> None:
        self.title = "Process Manager"