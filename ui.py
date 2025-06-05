import time
from process_manager.node import Watcher, Node
import subprocess

from textual.app import App, ComposeResult
from textual.widgets import Header, ListView, ListItem, Static, Label
from textual.reactive import reactive
from textual.containers import Horizontal, Vertical
# from rich.text import Text

        
class ProcessListItem(ListItem):
    def __init__(self, node: Node):
        self.node = node
        # Just directly use a string label
        super().__init__(
            Horizontal(
                Label(node.name, id="node_name"),
                Label("🟢" if node.is_alive() else "🔴", id="node_status"),
                id="list_item"
            )
        )

    
class Process_Manager_App(App):
    CSS_PATH = "manager.tcss"
    
    def __init__(self, watcher: Watcher, **kwargs):
        super().__init__(**kwargs)
        self.watcher = watcher
        self.detail_panel = Static("Select a process to see details.", expand=True)
        self.process_list_view = ListView(id="process_list")
        self.selected_index = reactive(0)
        self.period = 2
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield self.process_list_view
        # yield Horizontal(
        #     self.process_list_view,
        #     # Vertical(, id="list", expand=True),
        #     self.detail_panel,
        # )
    
    def on_mount(self) -> None:
        self.title = "Process Manager"
         # Populate the list
        self.refresh_process_list()
        # Update every 2 seconds
        self.set_interval(self.period, self.refresh_process_list)
        
    def refresh_process_list(self):
        self.process_list_view.clear()
        for process in self.watcher.processes:
            self.process_list_view.append(ProcessListItem(process))
        # self.update_detail_panel(self.selected_index)