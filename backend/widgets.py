
from . import period


# ============================== Base classes ==============================

class Widget:
    """
    Base class for all widgets.
    A widget is a exchangable UI component summarizing desired data for a given time period.
    On hover, it highlights related elements in the calendar.

    Widgets will look at the last `LOOKBACK` time periods to calculate the relevance of their data.
    """

    LOOKBACK = 4

    def __init__(self, period: period.Period) -> None:
        self._period = period

    def render(self) -> str:
        """
        Renders the widget as an HTML string.
        """
        raise NotImplementedError()
    
    def highlighted_classnames(self) -> list[str]:
        """
        Returns the class names to be highlighted on widget hover.
        """
        raise NotImplementedError()


class CounterWidget(Widget):
    """
    Widget that is counting things (holidays, series exceptions, etc).
    On hover, it highlights the related elements in the calendar.
    """


class DensityWidget(Widget):
    """
    Widget that shows density of something over a time period.
    On hover, it highlights the related elements in the calendar.
    """


# ============================== Subclasses ==============================

class EventDensityWidget(DensityWidget):
    """
    Widget that shows density of any events over a time period.
    On hover, it highlights the related events in the calendar.
    """

    def render(self) -> str:
        return "<div>Event Density Widget</div>"
