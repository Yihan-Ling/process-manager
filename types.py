from dataclasses import dataclass
from typing import Optional

from cyclonedds.idl import IdlStruct, types


@dataclass
class ProcessState(IdlStruct):
    alive:  bool
    timestamp: types.float64