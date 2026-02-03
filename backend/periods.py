from __future__ import annotations

from icalendar import Calendar, Component
from typing import Self
from datetime import date, datetime, timedelta


class Period:
    """
    A time period that can be displayed as one unit in the calendar.
    Can represent a week, month, year, etc.
    """

    @staticmethod
    def from_start_date(start_date: date, calendars: list[Calendar] = []):
        """
        Creates a Period of the given type that contains the given date.
        """
        raise NotImplementedError()

    @staticmethod
    def from_any_date(any_date: date, start_of_week: int = 0, calendars: list[Calendar] = []) -> Period:
        """
        Creates a Period of the given type that contains the given date.
        """
        raise NotImplementedError()
    
    def __init__(self, start_date: date, end_date: date, calendars: list[Calendar] = []):
        self._start_date = start_date
        self._end_date = end_date
        self._calendars = calendars
        self._components: list[Component] = []
        for cal in calendars:
            for c in cal.walk():
                if hasattr(c, 'DTSTART'):
                    dtstart: date | datetime = c.DTSTART  # type: ignore
                    if type(dtstart) is datetime:
                        event_date = dtstart.date()
                    else:  # Is already a date
                        event_date = dtstart
                    if start_date <= event_date <= end_date:
                        self._components.append(c)
    
    @property
    def start_date(self): return self._start_date
    @property
    def end_date(self): return self._end_date
    @property
    def components(self): return self._components

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
    def from_start_date(start_date: date, calendars: list[Calendar] = []) -> Period:
        """
        Creates a Period of the given type that contains the given date.
        """
        return WeekPeriod.from_any_date(start_date, start_of_week=start_date.weekday(), calendars=calendars)  # Trust start_date's weekday as start_of_week
    
    @staticmethod
    def from_any_date(any_date: date, start_of_week: int = 0, calendars: list[Calendar] = []) -> Period:
        """
        Creates a Period of the given type that contains the given date.
        """
        delta_days = (any_date.weekday() - start_of_week) % 7
        start_date = any_date - timedelta(days=delta_days)
        return WeekPeriod(start_date, start_of_week=start_of_week, calendars=calendars)
    
    def __init__(self, start_date: date, start_of_week: int = 0, calendars: list[Calendar] = []):
        delta_days = (start_date.weekday() - start_of_week) % 7
        start_date = start_date - timedelta(days=delta_days)
        end_date = start_date + timedelta(days=6)
        super().__init__(start_date, end_date, calendars=calendars)

    def _generate_day_html(self, day: date) -> str:
        today = date.today()
        day_class = "day-passed" if day < today else "day-today" if day == today else "day-future"
        day_events = [event for event in self._components if hasattr(event, 'DTSTART') 
                      and ((type(event.DTSTART) is datetime and event.DTSTART.date() == day) or  # type: ignore
                           (type(event.DTSTART) is date and event.DTSTART == day))]  # type: ignore
        events_html = ""
        for event in day_events:
            event_summary = event.get('summary', 'No Title')
            events_html += f'<div class="event">{event_summary}</div>'
        return (f'<div id="day-{day.isoformat()}" class="{day_class} day-container">'
                f'  <div class="day-header">'
                f'    <span class="day-header-date">{day.strftime("%d")}</span>'
                f'    <span class="day-header-dayname">{day.strftime("%a").replace(".", "")}</span>'
                f'  </div>'
                f'  <div class="day-strip">'
                f'    {events_html}'
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
    def from_start_date(start_date: date, calendars: list[Calendar] = []):
        """
        Creates a Period of the given type that contains the given date.
        """
        return MonthPeriod.from_any_date(start_date, calendars=calendars)              
    
    @staticmethod
    def from_any_date(any_date: date, start_of_week: int = 0, calendars: list[Calendar] = []) -> Period:
        """
        Creates a Period of the given type that contains the given date.
        """
        start_date = any_date.replace(day=1)
        return MonthPeriod(start_date, calendars=calendars)
    
    def __init__(self, start_date: date, calendars: list[Calendar] = []):
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
    def from_start_date(start_date: date, calendars: list[Calendar] = []) -> Period:
        """
        Creates a Period of the given type that contains the given date.
        """
        return YearPeriod.from_any_date(start_date, calendars=calendars)
    
    @staticmethod
    def from_any_date(any_date: date, start_of_week: int = 0, calendars: list[Calendar] = []) -> Period:
        """
        Creates a Period of the given type that contains the given date.
        """
        start_date = any_date.replace(month=1, day=1)
        return YearPeriod(start_date, calendars=calendars)
    
    def __init__(self, start_date: date, calendars: list[Calendar] = []):
        start_date = start_date.replace(month=1, day=1)
        end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
        super().__init__(start_date, end_date, calendars=calendars)
    
    def generate_html(self, widget_types: list[type]) -> str:
        """
        Generates the HTML representation of this month period.
        """
        raise NotImplementedError()