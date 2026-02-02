
from typing import Self
from datetime import datetime, timedelta


class Period:
    """
    A time period that can be displayed as one unit in the calendar.
    Can represent a week, month, year, etc.
    """
    
    def __init__(self, start: datetime, end: datetime):
        self._start = start
        self._end = end

    def get_previous(self) -> Self:
        """
        Returns the previous period of the same type.
        """
        delta = self._end - self._start + timedelta(seconds=1)
        new_end = self._start - timedelta(seconds=1)
        new_start = new_end - delta + timedelta(seconds=1)
        return self.__class__(new_start, new_end)

    def get_next(self) -> Self:
        """
        Returns the next period of the same type.
        """
        delta = self._end - self._start + timedelta(seconds=1)
        new_start = self._end + timedelta(seconds=1)
        new_end = new_start + delta - timedelta(seconds=1)
        return self.__class__(new_start, new_end)


class WeekPeriod(Period):
    """
    A week period.
    """
    
    def __init__(self, start: datetime, start_of_week: int = 0):
        start = start - timedelta(days=(start.weekday() - start_of_week) % 7)
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        super().__init__(start, end)


class MonthPeriod(Period):
    """
    A month period.
    """
    
    def __init__(self, start: datetime):
        start = start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1, day=31, hour=23, minute=59, second=59)
        else:
            next_month_start = start.replace(month=start.month + 1, day=1)
            end = next_month_start - timedelta(seconds=1)
        super().__init__(start, end)
        raise NotImplementedError()
    

class YearPeriod(Period):
    """
    A year period.
    """
    
    def __init__(self, start: datetime):
        start = start.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(year=start.year + 1) - timedelta(seconds=1)
        super().__init__(start, end)
        raise NotImplementedError()
