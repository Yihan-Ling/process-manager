import time
from process_manager.node import Watcher, Node
import subprocess

from textual.app import App, ComposeResult
from textual.widgets import Header, ListView, ListItem, Static, Label, DataTable, Log
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
        self.process_list_view = ListView(id="process_list")
        self.detail_panel = Log(id="detail_panel")
        self.stats = DataTable(id="table")
        self.selected_index = reactive(0)
        self.period = 2
        self.current_node = None 
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            yield self.process_list_view
            with Vertical(id= "right_panel"):
                yield self.detail_panel
                yield self.stats

    def on_mount(self) -> None:
        self.title = "Process Manager"
         # Populate the list
        self.refresh_process_list()
        # Update every 2 seconds
        self.set_interval(self.period, self.refresh_process_list)
        self.detail_panel.write("Select a process to see detail")
        self.stats.add_columns("Name", "Uptime", "Status")
        for node in self.watcher.processes:
            uptime = node.get_uptime()
            status = "Running" if node.is_alive() else "Terminated"
            self.stats.add_row(node.name, f"{uptime:.1f} s", status)
            
        self.set_interval(1, self.refresh_selected_logs)
        self.set_interval(1, self.refresh_stats)
        
    def refresh_process_list(self):
        self.process_list_view.clear()
        for process in self.watcher.processes:
            self.process_list_view.append(ProcessListItem(process))
        # self.update_detail_panel(self.selected_index)
        

    async def on_list_view_selected(self, message: ListView.Selected) -> None:
        item = message.item
        if isinstance(item, ProcessListItem):
            node: Node = item.node
            self.current_node = node
            self.refresh_selected_logs()  # immediate refresh when selected
            
    def refresh_selected_logs(self):
        if not self.current_node:
            return
        
        current_lines = self.detail_panel.lines
        new_lines = self.current_node.logs

        if len(current_lines) != len(new_lines):
            self.detail_panel.clear()
            for line in new_lines:
                self.detail_panel.write_line(line)
                
    def refresh_stats(self):
        self.stats.clear()
        for node in self.watcher.processes:
            uptime = node.get_uptime()
            uptime = f"{uptime:.1f} s"
            status = "Running" if node.is_alive() else "Terminated"
            self.stats.add_row(node.name, uptime, status)