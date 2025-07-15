from dataclasses import dataclass
from cyclonedds.idl import IdlStruct, types

@dataclass
class Heartbeat(IdlStruct):
    name: str
    timestamp: types.float64
    
@dataclass
class LogMessage(IdlStruct):
    name: str
    levelname: str
    message: str
    timestamp: types.float64