
import icalendar
from datetime import date, time, datetime
from dateutil.rrule import rrulestr, rrule, rruleset


class Component:
    """
    Represents a generic RFC 5545 iCalendar component and exposes commonly used
    fields as convenient properties.
    """

    def __init__(self, ical_component: icalendar.Component):
        self._ical_component = ical_component
    
    @property
    def uid(self) -> str:
        return str(self._ical_component.get('UID', ''))
    
    @property
    
