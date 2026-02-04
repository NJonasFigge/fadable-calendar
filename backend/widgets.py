
from datetime import date

from . import periods
from .period_db import PeriodDB


'''
d8888b.  .d8b.  .d8888. d88888b       .o88b. db       .d8b.  .d8888. .d8888. d88888b .d8888. 
88  `8D d8' `8b 88'  YP 88'          d8P  Y8 88      d8' `8b 88'  YP 88'  YP 88'     88'  YP 
88oooY' 88ooo88 `8bo.   88ooooo      8P      88      88ooo88 `8bo.   `8bo.   88ooooo `8bo.   
88~~~b. 88~~~88   `Y8b. 88~~~~~      8b      88      88~~~88   `Y8b.   `Y8b. 88~~~~~   `Y8b. 
88   8D 88   88 db   8D 88.          Y8b  d8 88booo. 88   88 db   8D db   8D 88.     db   8D 
Y8888P' YP   YP `8888Y' Y88888P       `Y88P' Y88888P YP   YP `8888Y' `8888Y' Y88888P `8888Y' 
'''


class Widget:
    """
    Base class for all widgets.
    A widget is a exchangable UI component summarizing desired data for a given time period.
    On hover, it highlights related elements in the calendar.

    Widgets will look at the last `LOOKBACK` time periods to calculate the relevance of their data.
    """

    LOOKBACK = 4
    
    class COLOR_TOKENS:
        NEUTRAL = 'neutral'
        SUCCESS = 'success'
        INFO = 'info'
        WARNING = 'warning'
        DANGER = 'danger'

    def _core(self, period: periods.Period) -> int | float | str:
        """
        Core logic of the widget that performs the calculation on a single period.
        To be implemented by subclasses.
        """
        raise NotImplementedError()

    def _highlights_as_html_attribute(self) -> str:
        highlights = " ".join(self.highlights)
        if not highlights:
            return ""
        return f' data-highlights="{highlights}"'
    
    @property
    def highlights(self) -> list[str]:
        """
        Returns the class names to be highlighted on widget hover.
        """
        raise NotImplementedError()

    def render(self, period_type: type, start_date: date, period_db: PeriodDB) -> str:
        """
        Renders the widget text.
        """
        raise NotImplementedError()

    def get_color_token(self, value: int | float | str) -> str:
        """
        Returns the CSS color token name based on the widget value.
        """
        return self.COLOR_TOKENS.NEUTRAL


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
            return "normal"
        else:
            return "low"


'''
db   db  .d88b.  db      d888888b d8888b.  .d8b.  db    db .d8888.  .o88b.  .d88b.  db    db d8b   db d888888b 
88   88 .8P  Y8. 88        `88'   88  `8D d8' `8b `8b  d8' 88'  YP d8P  Y8 .8P  Y8. 88    88 888o  88 `~~88~~' 
88ooo88 88    88 88         88    88   88 88ooo88  `8bd8'  `8bo.   8P      88    88 88    88 88V8o 88    88    
88~~~88 88    88 88         88    88   88 88~~~88    88      `Y8b. 8b      88    88 88    88 88 V8o88    88    
88   88 `8b  d8' 88booo.   .88.   88  .8D 88   88    88    db   8D Y8b  d8 `8b  d8' 88b  d88 88  V888    88    
YP   YP  `Y88P'  Y88888P Y888888P Y8888D' YP   YP    YP    `8888Y'  `Y88P'  `Y88P'  ~Y8888P' VP   V8P    YP    
'''

class HolidaysCountWidget(CountWidget):
    """
    Widget that counts holidays over a time period.
    On hover, it highlights the related holidays in the calendar.
    """

    def _core(self, period: periods.Period) -> int:
        return sum(1 for _, _, _, event, _ in period.timed_events if event.categories and "holiday" in (cat.lower() for cat in event.categories))
    
    @property
    def highlights(self) -> list[str]:
        return ['event-holiday']

    def render(self, period_type: type, start_date: date, period_db: PeriodDB) -> str:
        # - Get the period
        period = period_db.get(period_type, start_date)
        count = self._core(period)
        color_token = self.get_color_token(count)
        highlights_attr = self._highlights_as_html_attribute()
        return f'<span class="week-widget week-widget-holidays-count" data-color="{color_token}"{highlights_attr}>{count} holidays this week</span>'
    
    def get_color_token(self, value: int | float | str) -> str:
        if not isinstance(value, (int, float)):
            return self.COLOR_TOKENS.NEUTRAL  # Handle non-numeric values gracefully (not expected here)
        if value >= 1:
            return self.COLOR_TOKENS.SUCCESS
        else:
            return self.COLOR_TOKENS.NEUTRAL


'''
d88888b db    db  .o88b. d88888b d8888b. d888888b d888888b  .d88b.  d8b   db .d8888.  .o88b.  .d88b.  db    db d8b   db d888888b 
88'     `8b  d8' d8P  Y8 88'     88  `8D `~~88~~'   `88'   .8P  Y8. 888o  88 88'  YP d8P  Y8 .8P  Y8. 88    88 888o  88 `~~88~~' 
88ooooo  `8bd8'  8P      88ooooo 88oodD'    88       88    88    88 88V8o 88 `8bo.   8P      88    88 88    88 88V8o 88    88    
88~~~~~  .dPYb.  8b      88~~~~~ 88~~~      88       88    88    88 88 V8o88   `Y8b. 8b      88    88 88    88 88 V8o88    88    
88.     .8P  Y8. Y8b  d8 88.     88         88      .88.   `8b  d8' 88  V888 db   8D Y8b  d8 `8b  d8' 88b  d88 88  V888    88    
Y88888P YP    YP  `Y88P' Y88888P 88         YP    Y888888P  `Y88P'  VP   V8P `8888Y'  `Y88P'  `Y88P'  ~Y8888P' VP   V8P    YP    
'''

class ExceptionsCountWidget(CountWidget):
    """
    Widget that counts series exceptions over a time period.
    On hover, it highlights the related exceptions in the calendar.
    """

    def _core(self, period: periods.Period) -> int:
        return len(period.exception_dates)
    
    @property
    def highlights(self) -> list[str]:
        return ['event-exception']

    def render(self, period_type: type, start_date: date, period_db: PeriodDB) -> str:
        # - Get the period
        period = period_db.get(period_type, start_date)
        count = self._core(period)
        color_token = self.get_color_token(count)
        highlights_attr = self._highlights_as_html_attribute()
        return f'<span class="week-widget week-widget-exceptions-count" data-color="{color_token}"{highlights_attr}>{count} exceptions this week</span>'
    
    def get_color_token(self, value: int | float | str) -> str:
        if not isinstance(value, (int, float)):
            return self.COLOR_TOKENS.NEUTRAL  # Handle non-numeric values gracefully (not expected here)
        if value >= 1:
            return self.COLOR_TOKENS.WARNING
        elif value >= 5:
            return self.COLOR_TOKENS.DANGER
        else:
            return self.COLOR_TOKENS.NEUTRAL


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
        return sum(1 for _, _, _, _, _ in period.timed_events)
    
    @property
    def highlights(self) -> list[str]:
        return ['event']

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

        color_token = self.get_color_token(density)
        highlights_attr = self._highlights_as_html_attribute()
        return f'<span class="week-widget week-widget-event-density" data-color="{color_token}"{highlights_attr}>Event density: {predicate}</span>'

    def get_color_token(self, value: int | float | str) -> str:
        if not isinstance(value, (int, float)):
            return self.COLOR_TOKENS.NEUTRAL  # Handle non-numeric values gracefully (not expected here)
        if value >= 1.5:
            return self.COLOR_TOKENS.INFO
        elif value >= .8:
            return self.COLOR_TOKENS.NEUTRAL
        else:
            return self.COLOR_TOKENS.WARNING
