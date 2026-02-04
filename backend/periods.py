from __future__ import annotations

import ics
from typing import Self
from datetime import date, time, datetime, timedelta


class Period:
    """
    A time period that can be displayed as one unit in the calendar.
    Can represent a week, month, year, etc.
    """

    @staticmethod
    def from_start_date(start_date: date, calendars: list[ics.Calendar] = []):
        """
        Creates a Period of the given type that contains the given date.
        """
        raise NotImplementedError()

    @staticmethod
    def from_any_date(any_date: date, start_of_week: int = 0, calendars: list[ics.Calendar] = []) -> Period:
        """
        Creates a Period of the given type that contains the given date.
        """
        raise NotImplementedError()
    
    def __init__(self, start_date: date, end_date: date, calendars: list[ics.Calendar] = []):
        self._start_date = start_date
        self._end_date = end_date
        self._calendars = calendars
    
    @property
    def start_date(self): return self._start_date
    @property
    def end_date(self): return self._end_date
    @property
    def calendars(self): return self._calendars

    @property
    def previous_period(self) -> Self:
        """
        Returns the previous period of the same type.
        """
        delta = self._end_date - self._start_date + timedelta(days=1)
        previous_start_date = self._start_date - delta
        return self.from_start_date(previous_start_date, calendars=self._calendars)

    @property
    def next_period(self) -> Self:
        """
        Returns the next period of the same type.
        """
        delta = self._end_date - self._start_date + timedelta(days=1)
        next_start_date = self._start_date + delta
        return self.from_start_date(next_start_date, calendars=self._calendars)
    
    def generate_html(self, widget_types: list[type]) -> str:
        """
        Generates the HTML representation of this period.
        """
        raise NotImplementedError()


class WeekPeriod(Period):
    """
    A week period.
    """

    @staticmethod
    def from_start_date(start_date: date, calendars: list[ics.Calendar] = []) -> Period:
        """
        Creates a Period of the given type that contains the given date.
        """
        return WeekPeriod.from_any_date(start_date, start_of_week=start_date.weekday(), calendars=calendars)  # Trust start_date's weekday as start_of_week
    
    @staticmethod
    def from_any_date(any_date: date, start_of_week: int = 0, calendars: list[ics.Calendar] = []) -> Period:
        """
        Creates a Period of the given type that contains the given date.
        """
        delta_days = (any_date.weekday() - start_of_week) % 7
        start_date = any_date - timedelta(days=delta_days)
        return WeekPeriod(start_date, start_of_week=start_of_week, calendars=calendars)
    
    def __init__(self, start_date: date, start_of_week: int = 0, calendars: list[ics.Calendar] = []):
        delta_days = (start_date.weekday() - start_of_week) % 7
        start_date = start_date - timedelta(days=delta_days)
        end_date = start_date + timedelta(days=6)
        super().__init__(start_date, end_date, calendars=calendars)

    def _generate_day_strip_html(self, day: date) -> str:
        """
        Generates the HTML for the week strip.
        """
        day_events = [event for calendar in self._calendars for event in calendar.events if event.begin.date() == day]
        print(day_events)
        html = ''
        for event in day_events:
            if event.all_day:
                continue  # Skip all-day events for now
            else:
                event_start_time = event.begin.time()
                event_start_position = (event_start_time.hour * 60 + event_start_time.minute) / (24 * 60) * 100
                event_end_time = event.end.time()
                event_end_position = (event_end_time.hour * 60 + event_end_time.minute) / (24 * 60) * 100
                event_color = next((prop.value for prop in event.extra if prop.name == 'COLOR'), "#888888")
                html += (f'<div '
                         f'  class="event"'
                         f'  style="--data-start-position: {event_start_position}%; '
                         f'         --data-end-position: {event_end_position}%; '
                         f'         --data-color: {event_color}">'
                         f'  {event.name}'
                         f'</div>')
        return html

    def _generate_day_html(self, day: date) -> str:
        today = date.today()
        day_class = "day-passed" if day < today else "day-today" if day == today else "day-future"
        strip_html = self._generate_day_strip_html(day)
        return (f'<div id="day-{day.isoformat()}" class="{day_class} day-container">'
                f'  <div class="day-header">'
                f'    <span class="day-header-date">'
                f'      {day.strftime("%d")}'
                f'    </span>'
                f'    <span class="day-header-dayname">'
                f'      {day.strftime("%a").replace(".", "")}'
                f'    </span>'
                f'  </div>'
                f'  <div class="day-strip">'
                f'    {strip_html}'
                f'  </div>'
                f'</div>')
    
    def generate_html(self, widget_types: list[type]) -> str:
        """
        Generates the HTML representation of this week period.
        """
        html = []
        for day_offset in range(7):
            current_day = self._start_date + timedelta(days=day_offset)
            html.append(self._generate_day_html(current_day))
        return "\n".join(html)


class MonthPeriod(Period):
    """
    A month period.
    """

    @staticmethod
    def from_start_date(start_date: date, calendars: list[ics.Calendar] = []):
        """
        Creates a Period of the given type that contains the given date.
        """
        return MonthPeriod.from_any_date(start_date, calendars=calendars)              
    
    @staticmethod
    def from_any_date(any_date: date, start_of_week: int = 0, calendars: list[ics.Calendar] = []) -> Period:
        """
        Creates a Period of the given type that contains the given date.
        """
        start_date = any_date.replace(day=1)
        return MonthPeriod(start_date, calendars=calendars)
    
    def __init__(self, start_date: date, calendars: list[ics.Calendar] = []):
        start_date = start_date.replace(day=1)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1, day=31)
        else:
            next_month_start = start_date.replace(month=start_date.month + 1, day=1)
            end_date = next_month_start - timedelta(days=1)
        super().__init__(start_date, end_date, calendars=calendars)
    
    def generate_html(self, widget_types: list[type]) -> str:
        """
        Generates the HTML representation of this month period.
        """
        raise NotImplementedError()


class YearPeriod(Period):
    """
    A year period.
    """

    @staticmethod
    def from_start_date(start_date: date, calendars: list[ics.Calendar] = []) -> Period:
        """
        Creates a Period of the given type that contains the given date.
        """
        return YearPeriod.from_any_date(start_date, calendars=calendars)
    
    @staticmethod
    def from_any_date(any_date: date, start_of_week: int = 0, calendars: list[ics.Calendar] = []) -> Period:
        """
        Creates a Period of the given type that contains the given date.
        """
        start_date = any_date.replace(month=1, day=1)
        return YearPeriod(start_date, calendars=calendars)
    
    def __init__(self, start_date: date, calendars: list[ics.Calendar] = []):
        start_date = start_date.replace(month=1, day=1)
        end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
        super().__init__(start_date, end_date, calendars=calendars)
    
    def generate_html(self, widget_types: list[type]) -> str:
        """
        Generates the HTML representation of this month period.
        """
        raise NotImplementedError()