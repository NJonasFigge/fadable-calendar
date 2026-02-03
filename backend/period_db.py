from __future__ import annotations

from typing import Iterator
from datetime import date
from pathlib import Path
from icalendar import Calendar

from . import periods


class PeriodDB:
    """
    A database interface for storing and retrieving already instantiated Periods.
    """

    START_OF_WEEK = 0  # 0 = Monday, 6 = Sunday

    def __init__(self, calendars: list[Calendar] = []) -> None:
        self._periods: dict[type, dict[date, periods.Period]] = {}
        self._calendars = calendars

    def load_ical_files(self, filepaths: Iterator[Path]) -> None:
        """
        Creates a PeriodDB from a list of .ics file paths.
        """
        for filepath in filepaths:
            calendar = Calendar.from_ical(filepath.read_text())
            self._calendars.append(calendar) # type: ignore
    
    def get(self, period_type: type, around_date: date) -> periods.Period:
        """
        Creates or retrieves a Period containing the given date.
        """
        # - Ensure period_type dict exists
        if period_type not in self._periods:
            self._periods[period_type] = {}
        # - Create period if it does not exist
        if around_date not in self._periods[period_type]:
            self._periods[period_type][around_date] = period_type.from_any_date(around_date, self.START_OF_WEEK, calendars=self._calendars)
        # - Return the period
        return self._periods[period_type][around_date]