from dataclasses import dataclass
from typing import Optional

from cyclonedds.idl import IdlStruct, types


@dataclass
class Heartbeat(IdlStruct):
    name: str
    timestamp: types.float64
    
@dataclass
class LogMessage(IdlStruct):
    name: str         # Logger name (e.g., "dummy_processes.d_one")
    levelname: str    # "INFO", "WARNING", etc.
    message: str      # The log message
    timestamp: types.float64