from process_manager.node import Watcher, Node

from textual.app import App, ComposeResult
from textual.widgets import Header, ListView, ListItem, Label, DataTable, Log, Footer
from textual.reactive import reactive
from textual.containers import Horizontal, Vertical
from process_manager.log import logger
from process_manager.util import auto_default_logging

import sys

_log = logger(__file__)

class ProcessListItem(ListItem):
    def __init__(self, node: Node):
        self.node = node
        color = node.get_severity_color()
        node_status_dot = Label("●", id="node_status")
        node_status_dot.styles.color = color
        
        super().__init__(
            Horizontal(
                Label(node.name, id="node_name"),
                node_status_dot,
                id="list_item"
            )
        )

    
class Process_Manager_App(App):
    CSS_PATH = "manager.tcss"
    BINDINGS = [
        ("a", "toggle_logs", "Toggle All/Selected Prints"),
    ]
    
    def __init__(self, watcher: Watcher, log_server, **kwargs):
        super().__init__(**kwargs)
        self.watcher = watcher
        self.process_list_view = ListView(id="process_list")
        self.detail_panel = Log(id="detail_panel")
        self.stats = DataTable(id="table")
        self.detail_label = Label("Select a process to see detail", id="detail_label")
        self.selected_index = reactive(0)
        self.period = 1
        self.current_node = None
        self.show_all_logs = False
        self.log_server = log_server
    
    def exit(self) -> None:
        _log.info("Shutting down UI: stopping processes and log server...")

        self.watcher.stop_all()
        
        if hasattr(self, "log_server"):
            self.log_server.shutdown()
            self.log_server.server_close()
            
        # super().exit() 
        sys.exit()
 
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Horizontal():
            yield self.process_list_view
            with Vertical(id= "right_panel"):
                yield self.detail_label
                yield self.detail_panel
                yield self.stats


    def on_mount(self) -> None:
        self.title = "Process Manager"
        self.refresh_process_list()
        self.set_interval(self.period, self.refresh_process_list)
        self.stats.add_columns("Name", "Uptime", "Status", "Log Level")
        self.stats.zebra_stripes = True
        self.stats.cursor_type = "row"
            
        self.set_interval(self.period, lambda: self.call_later(self.refresh_selected_logs))
        self.set_interval(self.period, self.refresh_stats)
        
    def refresh_process_list(self):
        self.process_list_view.clear()
        for process in self.watcher.processes:
            self.process_list_view.append(ProcessListItem(process))

    async def on_list_view_selected(self, message: ListView.Selected) -> None:
        item = message.item
        if isinstance(item, ProcessListItem):
            node: Node = item.node
            self.current_node = node
            self.refresh_selected_logs() 
            
    def refresh_selected_logs(self):
        self.detail_panel.clear()
        if self.show_all_logs:
            self.detail_label.update("Showing all terminal prints")
            for line in self.watcher.logs:
                self.detail_panel.write_line(line)
        elif self.current_node:
            self.detail_label.update("Showing selected terminal prints")
            for line in self.current_node.logs:
                self.detail_panel.write_line(line)
            
    def refresh_stats(self):

        self.stats.clear()

        for node in self.watcher.processes:
            name = node.name
            uptime = f"{node.get_uptime():.1f} s"
            status = "Running" if node.is_alive() else "Terminated"
            log_level = node.log_severity

            self.stats.add_row(name, uptime, status, log_level)

        self.stats.action_scroll_bottom()
        
            
    def action_toggle_logs(self) -> None:
        self.show_all_logs = not self.show_all_logs
        self.refresh_selected_logs()
    
