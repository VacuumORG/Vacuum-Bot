import enum
from dataclasses import dataclass
from typing import Optional


class PomodoroState(enum.Enum):
    Working = enum.auto()
    Break = enum.auto()
    LongBreak = enum.auto()


class AlarmOptions(enum.Enum):
    Digital = enum.auto()
    Done = enum.auto()
    Kitchen = enum.auto()
    Simple = enum.auto()


@dataclass
class PomodoroSettings:
    work_time: Optional[int] = 25
    break_time: Optional[int] = 5
    long_break_time: Optional[int] = 15
    n_breaks: Optional[int] = 3
    alarm_sound: Optional[AlarmOptions] = AlarmOptions.Digital
    use_voices: Optional[bool] = False
