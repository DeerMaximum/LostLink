from enum import Enum
from dataclasses import dataclass

class ResultType(Enum):
    DELETED = 0
    ADDED = 1
    CHANGED = 2

@dataclass
class ScanResult:
    type: ResultType
    path: str
