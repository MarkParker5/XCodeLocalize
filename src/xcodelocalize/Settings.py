from typing import Optional
from enum import Enum
from dataclasses import dataclass

from .Strings import FileGroup, StringsFile


class LogLevel(str, Enum):
    progress = 'progress'
    errors = 'errors'
    group = 'group'
    string = 'string'
    
    @property
    def int_value(self) -> int:
        return list(LogLevel).index(self)
    
    def __ge__(self, other):
        return self.int_value >= other.int_value

@dataclass
class Settings:
    base_language: str = 'en'
    override: bool = False
    format_base: bool = False

    files: Optional[list[str]] = None # all
    keys: Optional[list[str]] = None # all
    languages: Optional[list[str]] = None # all

    log_level: LogLevel = LogLevel.string

Languages = dict[str, StringsFile]
SearchResult = dict[FileGroup, Languages]