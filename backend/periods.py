from __future__ import annotations

import ics
from typing import Self
from datetime import date, time, datetime, timedelta
from zoneinfo import ZoneInfo
from dateutil.rrule import rrulestr


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

    def _generate_day_strip_html(self, day: date) -> tuple[str, int]:
        """
        Generates the HTML for the week strip.
        """
        timed_events: list[tuple[int, int, ics.Event]] = []  # (start_minutes, end_minutes, event)
        
        for calendar in self._calendars:
            for event in calendar.events:
                if event.all_day:
                    continue  # Skip all-day events for now

                has_rrule = any(prop.name == 'RRULE' for prop in event.extra)
                if has_rrule:
                    rrule_prop = next(prop for prop in event.extra if prop.name == 'RRULE')
                    rule = rrulestr(rrule_prop.value, dtstart=event.begin.datetime)
                    exdates: set[datetime] = set()

                    # - Collect EXDATEs (exceptions to the recurrence rule)
                    for prop in event.extra:
                        # - Skip non-EXDATE properties
                        if prop.name != 'EXDATE':
                            continue

                        # - Parse EXDATE value(s)
                        tzid = None
                        if hasattr(prop, 'params') and 'TZID' in prop.params:  # Get timezone ID if available
                            tzid = prop.params['TZID'][0] if prop.params['TZID'] else None
                        tzinfo = ZoneInfo(tzid) if tzid else event.begin.datetime.tzinfo
                        if len(prop.value) == 8:
                            exdate = datetime.strptime(prop.value, "%Y%m%d").replace(tzinfo=tzinfo)  # Date only
                        else:
                            exdate = datetime.strptime(prop.value, "%Y%m%dT%H%M%S").replace(tzinfo=tzinfo)  # Date and time
                        exdates.add(exdate)
                    
                    # - Generate occurrences for this day
                    day_start = datetime.combine(day, time.min, tzinfo=event.begin.datetime.tzinfo)
                    day_end = datetime.combine(day, time.max, tzinfo=event.begin.datetime.tzinfo)

                    for occ_start in rule.between(day_start, day_end, inc=True):
                        # -  Skip if in exdates
                        if occ_start in exdates:
                            continue
                        
                        # - Calculate end time based on duration
                        occ_end = occ_start + event.duration
                        
                        # - Determine start and end minutes within the day
                        if occ_start.date() < day:  # Starts before this day
                            start_minutes = 0
                        else:                       # Starts on this day
                            start_minutes = occ_start.hour * 60 + occ_start.minute
                        if occ_end.date() > day:    # Ends after this day
                            end_minutes = 24 * 60
                        else:                       # Ends on this day
                            end_minutes = occ_end.hour * 60 + occ_end.minute
                        
                        # - Add to timed events
                        timed_events.append((start_minutes, end_minutes, event))
                else:
                    # - Non-recurring event
                    if event.begin.date() != day:
                        continue

                    # - Determine start and end minutes
                    event_start_time = event.begin.time()
                    event_end_time = event.end.time()
                    start_minutes = event_start_time.hour * 60 + event_start_time.minute
                    end_minutes = event_end_time.hour * 60 + event_end_time.minute

                    # - Add to timed events
                    timed_events.append((start_minutes, end_minutes, event))

        # - Sort events by start time, then by end time
        timed_events.sort(key=lambda item: (item[0], item[1]))

        # - Assign events to rows to avoid overlaps
        row_end_times: list[int] = []
        events_with_rows: list[tuple[int, int, ics.Event, int]] = []
        for start_minutes, end_minutes, event in timed_events:
            row_index = None

            # - Find a row for this event
            for idx, row_end in enumerate(row_end_times):
                if row_end <= start_minutes:
                    # - Can fit in this row
                    row_index = idx
                    row_end_times[idx] = end_minutes
                    break
            
            if row_index is None:
                # - Need a new row
                row_index = len(row_end_times)
                row_end_times.append(end_minutes)
            events_with_rows.append((start_minutes, end_minutes, event, row_index))
        
        # - Generate HTML
        html = ''
        for start_minutes, end_minutes, event, row_index in events_with_rows:
            event_start_position = start_minutes / (24 * 60) * 100
            event_end_position = end_minutes / (24 * 60) * 100
            event_color = next((prop.value for prop in event.extra if prop.name == 'COLOR'), "#888888")
            html += (f'<div '
                     f'  class="event"'
                     f'  style="--data-start-position: {event_start_position}%; '
                     f'         --data-end-position: {event_end_position}%; '
                     f'         --data-row: {row_index}; '
                     f'         --data-color: {event_color}">'
                     f'  {event.name}'
                     f'</div>')
        
        total_rows = max(1, len(row_end_times))
        return html, total_rows

    def _generate_day_html(self, day: date) -> str:
        today = date.today()
        day_class = "day-passed" if day < today else "day-today" if day == today else "day-future"
        strip_html, total_rows = self._generate_day_strip_html(day)
        return (f'<div id="day-{day.isoformat()}" class="{day_class} day-container">'
                f'  <div class="day-header">'
                f'    <span class="day-header-date">'
                f'      {day.strftime("%d")}'
                f'    </span>'
                f'    <span class="day-header-dayname">'
                f'      {day.strftime("%a").replace(".", "")}'
                f'    </span>'
                f'  </div>'
            f'  <div class="day-strip" style="--data-rows: {total_rows};">'
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