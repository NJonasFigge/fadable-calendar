
import icalendar
from datetime import date, time, datetime
from dateutil.rrule import rrulestr, rrule, rruleset

from .alarm import Alarm


class Event:
    """
    Represents an RFC 5545 iCalendar VEVENT component and exposes commonly used
    fields as convenient properties.
    """

    def __init__(self, ical_event: icalendar.Event):
        self._ical_event = ical_event
    
    @property
    def start(self) -> datetime:
        dtstart = self._ical_event.get('DTSTART')
        if type(dtstart) is date:
            return datetime.combine(dtstart, time.min)
        else:
            return dtstart
        
    @property
    def end(self) -> datetime:
        dtend = self._ical_event.get('DTEND')
        if type(dtend) is date:
            return datetime.combine(dtend, time.max)
        else:
            return dtend

    @property
    def is_all_day(self) -> bool:
        dtstart = self._ical_event.get('DTSTART')
        dtend = self._ical_event.get('DTEND')
        return type(dtstart) is date and type(dtend) is date
    
    @property
    def is_across_multiple_days(self) -> bool:
        return self.end.date() > self.start.date()
    
    @property
    def summary(self) -> str:
        return str(self._ical_event.get('SUMMARY', 'Untitled'))

    @property
    def uid(self) -> str:
        return str(self._ical_event.get('UID', ''))
    
    @property
    def recurrence_id(self) -> datetime | None:
        rec_id = self._ical_event.get('RECURRENCE-ID')
        if rec_id is None:
            return None
        if type(rec_id) is date:
            return datetime.combine(rec_id, time.min)
        else:
            return rec_id
    
    @property
    def classification(self) -> str:
        """
        Returns the CLASS property of the event (e.g., PUBLIC, PRIVATE, CONFIDENTIAL).
        Defaults to empty string if not present.
        """
        return str(self._ical_event.get('CLASS', ''))
    
    @property
    def created(self) -> datetime | None:
        created = self._ical_event.get('CREATED')
        if created is None:
            return None
        return created

    @property
    def last_modified(self) -> datetime | None:
        last_modified = self._ical_event.get('LAST-MODIFIED')
        if last_modified is None:
            return None
        return last_modified
    
    @property
    def sequence_revision(self) -> int:
        """
        Returns the SEQUENCE revision number of the event. This number
        is incremented each time the event is modified.
        Defaults to 0 if not present.
        """
        seq = self._ical_event.get('SEQUENCE')
        if seq is None:
            return 0
        return int(seq)
    
    @property
    def status(self) -> str:
        """
        Returns the STATUS property of the event (e.g., CONFIRMED, TENTATIVE, CANCELLED).
        Defaults to empty string if not present.
        """
        return str(self._ical_event.get('STATUS', ''))
    
    @property
    def transparency(self) -> str:
        """
        Returns the TRANSP property of the event (e.g., OPAQUE, TRANSPARENT).
        Defaults to empty string if not present.
        """
        return str(self._ical_event.get('TRANSP', ''))
    
    @property
    def alarms(self) -> list[Alarm]:
        """
        Returns a list of alarms associated with the event.
        """
        alarms = []
        for component in self._ical_event.subcomponents:
            if component.name == 'VALARM':
                alarms.append(Alarm(component))
        return alarms
    
    @property
    def recurrence_rule(self) -> rrule | rruleset | None:
        """
        Returns the RRULE property of the event as a dictionary.
        """
        rrule = self._ical_event.get('RRULE')
        if rrule is None:
            return None
        else:
            return rrulestr(rrule, dtstart=self.start)
        
    def capture_recurrences(self, from_dt: datetime, to_dt: datetime) -> list[datetime]:
        """
        Returns a list of occurrence start datetimes between the given start and end datetimes.
        If the event is not recurring, returns the event start if it falls within the range.
        """
        occurrences = []
        rrule = self.recurrence_rule
        if rrule is None:
            # Non-recurring event
            if from_dt <= self.start <= to_dt or from_dt <= self.end <= to_dt:  # Event ends or starts within range
                occurrences.append(self.start)
        else:
            # Recurring event
            for occ in rrule.between(from_dt, to_dt, inc=True):
                occurrences.append(occ)
        return occurrences
