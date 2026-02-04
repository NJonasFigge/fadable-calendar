
from datetime import date

from . import periods
from .period_db import PeriodDB


'''
db   d8b   db d888888b d8888b.  d888b  d88888b d888888b 
88   I8I   88   `88'   88  `8D 88' Y8b 88'     `~~88~~' 
88   I8I   88    88    88   88 88      88ooooo    88    
Y8   I8I   88    88    88   88 88  ooo 88~~~~~    88    
`8b d8'8b d8'   .88.   88  .8D 88. ~8~ 88.        88    
 `8b8' `8d8'  Y888888P Y8888D'  Y888P  Y88888P    YP    
'''


class Widget:
    """
    Base class for all widgets.
    A widget is a exchangable UI component summarizing desired data for a given time period.
    On hover, it highlights related elements in the calendar.

    Widgets will look at the last `LOOKBACK` time periods to calculate the relevance of their data.
    """

    LOOKBACK = 4

    def _core(self, period: periods.Period) -> int | float | str:
        """
        Core logic of the widget that performs the calculation on a single period.
        To be implemented by subclasses.
        """
        raise NotImplementedError()

    def render(self, period_type: type, start_date: date, period_db: PeriodDB) -> str:
        """
        Renders the widget text.
        """
        raise NotImplementedError()
    
    def highlighted_classnames(self) -> list[str]:
        """
        Returns the class names to be highlighted on widget hover.
        """
        raise NotImplementedError()


class CountWidget(Widget):
    """
    Widget that is counting things (holidays, series exceptions, etc).
    On hover, it highlights the related elements in the calendar.
    """


class DensityWidget(Widget):
    """
    Widget that shows density of something over a time period.
    On hover, it highlights the related elements in the calendar.
    """

    def _core(self, period: periods.Period) -> int | float:  # Removing str as a possible return type
        raise NotImplementedError()

    def _calculate_density(self, this_period: periods.Period, lookback_periods: list[periods.Period]) -> float:
        """
        Calculates the density for the given period based on lookback periods.
        """
        this_result = self._core(this_period)
        lookback_results = [self._core(p) for p in lookback_periods]
        average_lookback = sum(lookback_results) / len(lookback_results) if len(lookback_results) > 0 else 1.
        return this_result / average_lookback if average_lookback > 0 else 1.

    def _get_predicate(self, density: float) -> str:
        """
        Determines the predicate for the given density value.
        """
        if density >= 1.5:
            return "high"
        elif density >= .8:
            return "medium"
        else:
            return "low"


'''
d88888b db    db d88888b d8b   db d888888b d8888b. d88888b d8b   db .d8888. d888888b d888888b db    db
88'     88    88 88'     888o  88 `~~88~~' 88  `8D 88'     888o  88 88'  YP   `88'   `~~88~~' `8b  d8'
88ooooo Y8    8P 88ooooo 88V8o 88    88    88   88 88ooooo 88V8o 88 `8bo.      88       88     `8bd8' 
88~~~~~ `8b  d8' 88~~~~~ 88 V8o88    88    88   88 88~~~~~ 88 V8o88   `Y8b.    88       88       88   
88.      `8bd8'  88.     88  V888    88    88  .8D 88.     88  V888 db   8D   .88.      88       88   
Y88888P    YP    Y88888P VP   V8P    YP    Y8888D' Y88888P VP   V8P `8888Y' Y888888P    YP       YP   
'''


class EventDensityWidget(DensityWidget):
    """
    Widget that shows density of any events over a time period.
    On hover, it highlights the related events in the calendar.
    """

    def _core(self, period: periods.Period) -> int:
        return sum(1 for _, _, _, _ in period.timed_events)

    def render(self, period_type: type, start_date: date, period_db: PeriodDB) -> str:
        # - Get the period
        period = period_db.get(period_type, start_date)
        
        # - Collect lookback periods
        lookback_periods = []
        prev_period = period
        for _ in range(self.LOOKBACK):
            prev_period = prev_period.previous_period
            lookback_periods.append(prev_period)
        
        density = self._calculate_density(period, lookback_periods)
        predicate = self._get_predicate(density)

        return f'<span class="week-widget week-widget-event-density">Event density: {predicate}</span>'
    
    def highlighted_classnames(self) -> list[str]:
        return ["event"]
