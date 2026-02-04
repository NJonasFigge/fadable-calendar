from __future__ import annotations

import ics
from typing import Self
from datetime import date, time, datetime, timedelta
from zoneinfo import ZoneInfo
from dateutil.rrule import rrulestr


'''
d8888b. d88888b d8888b. d888888b  .d88b.  d8888b. 
88  `8D 88'     88  `8D   `88'   .8P  Y8. 88  `8D 
88oodD' 88ooooo 88oobY'    88    88    88 88   88 
88~~~   88~~~~~ 88`8b      88    88    88 88   88 
88      88.     88 `88.   .88.   `8b  d8' 88  .8D 
88      Y88888P 88   YD Y888888P  `Y88P'  Y8888D' 
'''


class Period:
    """
    A time period that can be displayed as one unit in the calendar.
    Can represent a week, month, year, etc.
    """

    @staticmethod
    def from_start_date(start_date: date, calendars: list[ics.Calendar] = [],
                        calendar_colors: list[str] | None = None):
        """
        Creates a Period of the given type that contains the given date.
        """
        raise NotImplementedError()

    @staticmethod
    def from_any_date(any_date: date, start_of_week: int = 0, calendars: list[ics.Calendar] = [],
                      calendar_colors: list[str] | None = None):
        """
        Creates a Period of the given type that contains the given date.
        """
        raise NotImplementedError()
    
    def __init__(self, start_date: date, end_date: date, calendars: list[ics.Calendar] = [], 
                 calendar_colors: list[str] | None = None):
        self._start_date = start_date
        self._end_date = end_date
        self._calendars = calendars  # Handles of calendars that also apply to all other periods
        self._calendar_colors = calendar_colors if calendar_colors is not None else ['#777777'] * len(calendars)
        self._exception_dates: set[datetime] = set()  # Exception dates for recurring events
    
    @property
    def start_date(self): return self._start_date
    @property
    def end_date(self): return self._end_date

    @property
    def previous_period(self) -> Self:
        """
        Returns the previous period of the same type.
        """
        delta = self._end_date - self._start_date + timedelta(days=1)
        previous_start_date = self._start_date - delta
        return self.from_start_date(previous_start_date, calendars=self._calendars,
                                    calendar_colors=self._calendar_colors)

    @property
    def next_period(self) -> Self:
        """
        Returns the next period of the same type.
        """
        delta = self._end_date - self._start_date + timedelta(days=1)
        next_start_date = self._start_date + delta
        return self.from_start_date(next_start_date, calendars=self._calendars,
                                    calendar_colors=self._calendar_colors)
    
    @property
    def timed_events(self) -> list[tuple[date, int, int, ics.Event, str]]:
        """
        Returns a list of timed events occurring within this period.
        Each event is represented as a tuple of (occurrence_date, start_minutes, end_minutes, event, color),
        where occurrence_date is the date of the occurrence, and start_minutes and end_minutes
        represent the start and end times of the event in minutes from midnight.
        """
        timed_events: list[tuple[date, int, int, ics.Event, str]] = []  # (occurrence_date, start_minutes, end_minutes, event, color)

        for calendar, color in zip(self._calendars, self._calendar_colors):
            for event in calendar.events:
                if event.all_day:
                    continue  # Skip all-day events for now

                has_rrule = any(prop.name == 'RRULE' for prop in event.extra)
                if has_rrule:
                    # - Recurring event
                    rrule_prop = next(prop for prop in event.extra if prop.name == 'RRULE')
                    rule = rrulestr(rrule_prop.value, dtstart=event.begin.datetime)

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
                        
                        # - Add to exception dates if within this period
                        if self._start_date <= exdate.date() <= self._end_date:
                            self._exception_dates.add(exdate)
                    
                    # - Generate occurrences for this period
                    period_start = datetime.combine(self._start_date, time.min, tzinfo=event.begin.datetime.tzinfo)
                    period_end = datetime.combine(self._end_date, time.max, tzinfo=event.begin.datetime.tzinfo)

                    for occ_start in rule.between(period_start, period_end, inc=True):
                        # -  Skip if in exdates
                        if occ_start in self._exception_dates:
                            continue
                        
                        # - Calculate end time based on duration
                        occ_end = occ_start + event.duration
                        
                        # - Determine start and end minutes within the day
                        if occ_start.date() < self._start_date:  # Starts before this period
                            start_minutes = 0
                        else:                       # Starts on this day
                            start_minutes = occ_start.hour * 60 + occ_start.minute
                        if occ_end.date() > self._end_date:    # Ends after this period
                            end_minutes = 24 * 60
                        else:                       # Ends on this day
                            end_minutes = occ_end.hour * 60 + occ_end.minute
                        
                        # - Add to timed events
                        timed_events.append((occ_start.date(), start_minutes, end_minutes, event, color))
                else:
                    # - Non-recurring event
                    if event.end.date() < self._start_date or event.begin.date() > self._end_date:
                        continue

                    # - Determine start and end minutes
                    event_start_time = event.begin.time()
                    event_end_time = event.end.time()
                    start_minutes = event_start_time.hour * 60 + event_start_time.minute
                    end_minutes = event_end_time.hour * 60 + event_end_time.minute

                    # - Add to timed events
                    timed_events.append((event.begin.date(), start_minutes, end_minutes, event, color))

        # - Sort events by start time, then by end time
        timed_events.sort(key=lambda item: (item[0], item[1], item[2]))
        return timed_events
    
    @property
    def exception_dates(self) -> set[datetime]:
        """
        Returns the set of exception dates for recurring events in this period.
        """
        return self._exception_dates
    
    def generate_html(self, widget_types: list[type]) -> str:
        """
        Generates the HTML representation of this period.
        """
        raise NotImplementedError()


'''
db   d8b   db d88888b d88888b db   dD d8888b. d88888b d8888b. d888888b  .d88b.  d8888b. 
88   I8I   88 88'     88'     88 ,8P' 88  `8D 88'     88  `8D   `88'   .8P  Y8. 88  `8D 
88   I8I   88 88ooooo 88ooooo 88,8P   88oodD' 88ooooo 88oobY'    88    88    88 88   88 
Y8   I8I   88 88~~~~~ 88~~~~~ 88`8b   88~~~   88~~~~~ 88`8b      88    88    88 88   88 
`8b d8'8b d8' 88.     88.     88 `88. 88      88.     88 `88.   .88.   `8b  d8' 88  .8D 
 `8b8' `8d8'  Y88888P Y88888P YP   YD 88      Y88888P 88   YD Y888888P  `Y88P'  Y8888D' 
'''


class WeekPeriod(Period):
    """
    A week period.
    """

    @staticmethod
    def from_start_date(start_date: date, calendars: list[ics.Calendar] = [],
                        calendar_colors: list[str] | None = None):
        """
        Creates a Period of the given type that contains the given date.
        """
        return WeekPeriod.from_any_date(start_date, start_of_week=start_date.weekday(), calendars=calendars,
                                        calendar_colors=calendar_colors)  # Trust start_date's weekday as start_of_week
    
    @staticmethod
    def from_any_date(any_date: date, start_of_week: int = 0, calendars: list[ics.Calendar] = [],
                     calendar_colors: list[str] | None = None):
        """
        Creates a Period of the given type that contains the given date.
        """
        delta_days = (any_date.weekday() - start_of_week) % 7
        start_date = any_date - timedelta(days=delta_days)
        return WeekPeriod(start_date, start_of_week=start_of_week, calendars=calendars,
                          calendar_colors=calendar_colors)
    
    def __init__(self, start_date: date, start_of_week: int = 0, calendars: list[ics.Calendar] = [],
                 calendar_colors: list[str] | None = None):
        delta_days = (start_date.weekday() - start_of_week) % 7
        start_date = start_date - timedelta(days=delta_days)
        end_date = start_date + timedelta(days=6)
        super().__init__(start_date, end_date, calendars=calendars, calendar_colors=calendar_colors)
    
    def _generate_day_strip_html(self, day: date) -> tuple[str, int]:
        """
        Generates the HTML for the week strip.
        """
        row_end_times: list[int] = []
        events_with_rows: list[tuple[int, int, ics.Event, int, str]] = []

        # - Assign events to rows to avoid overlaps
        for occ_date, start_minutes, end_minutes, event, color in self.timed_events:
            # - Skip events not on this day
            if occ_date != day:
                continue

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
            events_with_rows.append((start_minutes, end_minutes, event, row_index, color))
        
        # - Generate HTML
        html = ''
        for start_minutes, end_minutes, event, row_index, color in events_with_rows:
            event_start_position = start_minutes / (24 * 60) * 100
            event_end_position = end_minutes / (24 * 60) * 100
            event_color = next((prop.value for prop in event.extra if prop.name == 'COLOR'), color)
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


'''
.88b  d88.  .d88b.  d8b   db d888888b db   db d8888b. d88888b d8888b. d888888b  .d88b.  d8888b. 
88'YbdP`88 .8P  Y8. 888o  88 `~~88~~' 88   88 88  `8D 88'     88  `8D   `88'   .8P  Y8. 88  `8D 
88  88  88 88    88 88V8o 88    88    88ooo88 88oodD' 88ooooo 88oobY'    88    88    88 88   88 
88  88  88 88    88 88 V8o88    88    88~~~88 88~~~   88~~~~~ 88`8b      88    88    88 88   88 
88  88  88 `8b  d8' 88  V888    88    88   88 88      88.     88 `88.   .88.   `8b  d8' 88  .8D 
YP  YP  YP  `Y88P'  VP   V8P    YP    YP   YP 88      Y88888P 88   YD Y888888P  `Y88P'  Y8888D' 
'''


class MonthPeriod(Period):
    """
    A month period.
    """

    @staticmethod
    def from_start_date(start_date: date, calendars: list[ics.Calendar] = [],
                        calendar_colors: list[str] | None = None):
        """
        Creates a Period of the given type that contains the given date.
        """
        return MonthPeriod.from_any_date(start_date, calendars=calendars)              
    
    @staticmethod
    def from_any_date(any_date: date, start_of_week: int = 0, calendars: list[ics.Calendar] = [],
                      calendar_colors: list[str] | None = None):
        """
        Creates a Period of the given type that contains the given date.
        """
        start_date = any_date.replace(day=1)
        return MonthPeriod(start_date, calendars=calendars, calendar_colors=calendar_colors)
    
    def __init__(self, start_date: date, calendars: list[ics.Calendar] = [],
                 calendar_colors: list[str] | None = None):
        start_date = start_date.replace(day=1)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1, day=31)
        else:
            next_month_start = start_date.replace(month=start_date.month + 1, day=1)
            end_date = next_month_start - timedelta(days=1)
        super().__init__(start_date, end_date, calendars=calendars, calendar_colors=calendar_colors)
    
    def generate_html(self, widget_types: list[type]) -> str:
        """
        Generates the HTML representation of this month period.
        """
        raise NotImplementedError()
    

'''
db    db d88888b  .d8b.  d8888b. d8888b. d88888b d8888b. d888888b  .d88b.  d8888b. 
`8b  d8' 88'     d8' `8b 88  `8D 88  `8D 88'     88  `8D   `88'   .8P  Y8. 88  `8D 
 `8bd8'  88ooooo 88ooo88 88oobY' 88oodD' 88ooooo 88oobY'    88    88    88 88   88 
   88    88~~~~~ 88~~~88 88`8b   88~~~   88~~~~~ 88`8b      88    88    88 88   88 
   88    88.     88   88 88 `88. 88      88.     88 `88.   .88.   `8b  d8' 88  .8D 
   YP    Y88888P YP   YP 88   YD 88      Y88888P 88   YD Y888888P  `Y88P'  Y8888D' 
'''


class YearPeriod(Period):
    """
    A year period.
    """

    @staticmethod
    def from_start_date(start_date: date, calendars: list[ics.Calendar] = [],
                        calendar_colors: list[str] | None = None):
        """
        Creates a Period of the given type that contains the given date.
        """
        return YearPeriod.from_any_date(start_date, calendars=calendars)
    
    @staticmethod
    def from_any_date(any_date: date, start_of_week: int = 0, calendars: list[ics.Calendar] = [],
                      calendar_colors: list[str] | None = None):
        """
        Creates a Period of the given type that contains the given date.
        """
        start_date = any_date.replace(month=1, day=1)
        return YearPeriod(start_date, calendars=calendars, calendar_colors=calendar_colors)
    
    def __init__(self, start_date: date, calendars: list[ics.Calendar] = [],
                 calendar_colors: list[str] | None = None):
        start_date = start_date.replace(month=1, day=1)
        end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
        super().__init__(start_date, end_date, calendars=calendars, calendar_colors=calendar_colors)
    
    def generate_html(self, widget_types: list[type]) -> str:
        """
        Generates the HTML representation of this month period.
        """
        raise NotImplementedError()