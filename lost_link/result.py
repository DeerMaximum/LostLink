from dataclasses import dataclass
from datetime import datetime


@dataclass
class ResultEntry:
    filename: str
    last_modified: datetime
    source: str
    open_url: str

    def __lt__(self, other):
        return self.last_modified < other.last_modified