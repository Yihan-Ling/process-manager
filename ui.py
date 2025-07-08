from process_manager.node import Watcher, Node

from textual.app import App, ComposeResult
from textual.widgets import Header, ListView, ListItem, Label, DataTable, Log, Footer
from textual.reactive import reactive
from textual.containers import Horizontal, Vertical
from process_manager.log import logger
from process_manager.util import auto_default_logging

from rich.text import Text

import sys

_log = logger(__file__)

# class ProcessListItem(ListItem):
#     def __init__(self, node: Node):
#         self.node = node
#         color = node.get_severity_color()
#         node_status_dot = Label("●", id="node_status")
#         node_status_dot.styles.color = color
        
#         super().__init__(
#             Horizontal(
#                 Label(node.name, id="node_name"),
#                 node_status_dot,
#                 id="list_item"
#             )
#         )

    
class Process_Manager_App(App):
    CSS_PATH = "manager.tcss"
    BINDINGS = [
        ("a", "toggle_logs", "Toggle All/Selected Prints"),
    ]
    
    def __init__(self, watcher: Watcher, log_server, **kwargs):
        super().__init__(**kwargs)
        self.watcher = watcher
        self.process_list = DataTable(id="process_list")
        self.detail_panel = Log(id="detail_panel")
        self.main_log = Log(id="main_log")
        # self.stats = DataTable(id="table")
        self.detail_label = Label("Select a process to see detail", id="detail_label")
        self.main_label = Label("Process Manager Logs", id="main_label")
        self.selected_index = reactive(0)
        self.period = 1
        self.current_node = None
        self.show_all_logs = False
        self.log_server = log_server
    
    def exit(self) -> None:
        _log.info("Shutting down UI: stopping processes and log server...")
        sys.exit()
        self.watcher.stop_all()
        
        if hasattr(self, "log_server"):
            self.log_server.shutdown()
            self.log_server.server_close()
            
        # super().exit() 
        
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Horizontal():
            yield self.process_list
            with Vertical(id= "right_panel"):
                yield self.detail_label
                yield self.detail_panel
                yield self.main_label
                yield self.main_log


    def on_mount(self) -> None:
        self.title = "Process Manager"
        self.initialize_process_list()
        # self.stats.add_columns("Name", "Uptime", "Status", "Log Level")
        # self.stats.zebra_stripes = True
        # self.stats.cursor_type = "row"
        
        self.set_interval(self.period, self.refresh_process_list)    
        self.set_interval(self.period, lambda: self.call_later(self.refresh_selected_logs))
        self.set_interval(self.period, self.refresh_main_logs)
    
    def initialize_process_list(self):
        self.process_list.add_columns("Name", "Uptime", "Status", "Log Level")
        self.process_list.zebra_stripes = True
        self.process_list.cursor_type = "row"
        
    def refresh_process_list(self):
        
        existing_keys = self.process_list.rows
        
        for row_index, node in enumerate(self.watcher.processes):
            name = node.name
            uptime = f"{node.get_uptime():.1f} s"
            status = "Running" if node.is_alive() else "Terminated"
            color = node.get_severity_color()
            log_level = Text(f"{node.log_severity}", style=f"{color}")
            
           
            # node_status_label = Text("●", style=f"{color}")
            # Add row if missing
            if row_index >= len(existing_keys):
                self.process_list.add_row(name, uptime, status, log_level)
                continue
            
            self.process_list.update_cell_at((row_index, 0), name)
            self.process_list.update_cell_at((row_index, 1), uptime)
            self.process_list.update_cell_at((row_index, 2), status)
            self.process_list.update_cell_at((row_index, 3), log_level)

    async def on_data_table_row_selected(self, message: DataTable.RowSelected) -> None:
        cursor_row = message.cursor_row
        row_key = message.row_key
        row = self.process_list.get_row(row_key)

        if row is None or len(row) == 0:
            return

        selected_name = row[0]  # First column is the node name

        # Match node by name
        for node in self.watcher.processes:
            if node.name == selected_name:
                self.current_node = node
                self.refresh_selected_logs()
                break
            
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
                
                
    def refresh_main_logs(self):
        self.main_log.clear()
        for line in self.watcher.main_logs:
            self.main_log.write_line(line)
            
    # def refresh_stats(self):

    #     self.stats.clear()

    #     for node in self.watcher.processes:
    #         name = node.name
    #         uptime = f"{node.get_uptime():.1f} s"
    #         status = "Running" if node.is_alive() else "Terminated"
    #         log_level = node.log_severity

    #         self.stats.add_row(name, uptime, status, log_level)

    #     self.stats.action_scroll_bottom()
        
            
    def action_toggle_logs(self) -> None:
        self.show_all_logs = not self.show_all_logs
        self.refresh_selected_logs()
    
