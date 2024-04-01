import enum


class GroupMode(str, enum.Enum):
    Minute = "1m"
    Hour = "1h"
    Day = "1d"
    Week = "7d"
    Month = "1mo"
    Year = "1y"
