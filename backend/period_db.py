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

    def __init__(self, calendars: list[ics.Calendar] | None = None, calendar_colors: list[str] | None = None):
        self._periods: dict[type, dict[date, periods.Period]] = {}
        self._calendars = list(calendars) if calendars is not None else []
        self._color_generator = self._generate_random_calendar_colors()
        if calendar_colors is None:
            self._calendar_colors = [next(self._color_generator) for _ in self._calendars]
        else:
            self._calendar_colors = list(calendar_colors)
        if len(self._calendar_colors) < len(self._calendars):
            missing = len(self._calendars) - len(self._calendar_colors)
            self._calendar_colors.extend(next(self._color_generator) for _ in range(missing))

    def load_ical_files(self, filepaths: Iterator[Path], calendar_colors: Iterator[str] | None = None):
        """
        Creates a PeriodDB from a list of .ics file paths.
        """
        colors_iter = iter(calendar_colors) if calendar_colors is not None else None
        for filepath in filepaths:
            if colors_iter is None:
                calendar_color = next(self._color_generator)
            else:
                try:
                    calendar_color = next(colors_iter)
                except StopIteration:
                    calendar_color = next(self._color_generator)
            calendar = ics.Calendar(filepath.read_text())
            self._calendars.append(calendar) # type: ignore
            self._calendar_colors.append(calendar_color)

    def load_from_urls(self, urls: Iterator[str]) -> None:
        """
        Creates a PeriodDB from a list of .ics URLs.
        """
        for url in urls:
            with urlopen(url) as response:
                calendar = ics.Calendar(response.read().decode("utf-8"))
            self._calendars.append(calendar) # type: ignore
            self._calendar_colors.append(next(self._color_generator))
    
    def get(self, period_type: type, around_date: date) -> periods.Period:
        """
        Creates or retrieves a Period containing the given date.
        """
        # - Ensure period_type dict exists
        if period_type not in self._periods:
            self._periods[period_type] = {}
        # - Create period if it does not exist
        if around_date not in self._periods[period_type]:
            self._periods[period_type][around_date] = period_type.from_any_date(
                around_date,
                self.START_OF_WEEK,
                calendars=self._calendars,
                calendar_colors=self._calendar_colors,
            )
        # - Return the period
        return self._periods[period_type][around_date]