from __future__ import annotations

import ics
import random
from typing import Iterator
from datetime import date
from pathlib import Path
from urllib.request import urlopen

from . import periods


class PeriodDB:
    """
    A database interface for storing and retrieving already instantiated Periods.
    """

    @staticmethod
    def _generate_random_calendar_colors() -> Iterator[str]:
        while True:
            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            yield color

    START_OF_WEEK = 0  # 0 = Monday, 6 = Sunday

    def __init__(self, calendars: list[ics.Calendar] = [], calendar_colors: Iterator[str] | None = None):
        self._periods: dict[type, dict[date, periods.Period]] = {}
        self._calendars = calendars
        self._calendar_colors: Iterator[str] = (calendar_colors if calendar_colors is not None
                                                else self._generate_random_calendar_colors())

    def load_ical_files(self, filepaths: Iterator[Path], calendar_colors: Iterator[str] | None = None):
        """
        Creates a PeriodDB from a list of .ics file paths.
        """
        if calendar_colors is None:
            calendar_colors = self._generate_random_calendar_colors()
        for filepath, calendar_color in zip(filepaths, calendar_colors):
            calendar = ics.Calendar(filepath.read_text())
            self._calendars.append(calendar) # type: ignore
            self._calendar_colors.send(calendar_color)

    def load_from_urls(self, urls: Iterator[str]) -> None:
        """
        Creates a PeriodDB from a list of .ics URLs.
        """
        for url in urls:
            with urlopen(url) as response:
                calendar = ics.Calendar(response.read().decode("utf-8"))
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