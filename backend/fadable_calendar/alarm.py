
import icalendar


class Alarm:
    """
    A wrapper class for an iCalendar VALARM component, providing access to its
    properties.
    """
    
    def __init__(self, ical_alarm: icalendar.Alarm):
        self._ical_alarm = ical_alarm

    @property
    def action(self) -> str:
        return str(self._ical_alarm.get('ACTION', ''))

    @property
    def trigger(self) -> str:
        trigger = self._ical_alarm.get('TRIGGER')
        return str(trigger) if trigger else ''
    
    @property
    def description(self) -> str:
        return str(self._ical_alarm.get('DESCRIPTION', ''))
