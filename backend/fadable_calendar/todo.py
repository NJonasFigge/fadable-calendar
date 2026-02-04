from __future__ import annotations

import icalendar
from datetime import date, time, datetime
from dateutil.rrule import rrulestr, rrule, rruleset

from .alarm import Alarm


class ToDo:
    """
    Represents an RFC 5545 iCalendar VTODO component and exposes commonly used
    fields as convenient properties.
    """

    def __init__(self, ical_todo: icalendar.Todo):
        self._ical_todo = ical_todo
    
    @property
    def due(self) -> datetime | None:
        dtdue = self._ical_todo.get('DUE')
        if dtdue is None:
            return None
        if type(dtdue) is date:
            return datetime.combine(dtdue, time.max)
        else:
            return dtdue

    @property
    def summary(self) -> str:
        return str(self._ical_todo.get('SUMMARY', 'Untitled'))

    @property
    def uid(self) -> str:
        return str(self._ical_todo.get('UID', ''))
    
    'class / completed / created / description / dtstart / geo / last-mod / location / organizer / percent / priority / recurid / seq / status / summary / url /'

    @property
    def is_completed(self) -> bool:
        status = self._ical_todo.get('STATUS')
        return str(status).upper() == 'COMPLETED'
    
    @property
    def created(self) -> datetime | None:
        dtcreated = self._ical_todo.get('CREATED')
        if dtcreated is None:
            return None
        if type(dtcreated) is date:
            return datetime.combine(dtcreated, time.min)
        else:
            return dtcreated
