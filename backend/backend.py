
from dataclasses import dataclass
from datetime import date

from . import periods
from . import widgets
from .period_db import PeriodDB


'''
d8888b.  .d8b.   .o88b. db   dD d88888b d8b   db d8888b. .d8888. d888888b  .d8b.  d888888b d88888b 
88  `8D d8' `8b d8P  Y8 88 ,8P' 88'     888o  88 88  `8D 88'  YP `~~88~~' d8' `8b `~~88~~' 88'     
88oooY' 88ooo88 8P      88,8P   88ooooo 88V8o 88 88   88 `8bo.      88    88ooo88    88    88ooooo 
88~~~b. 88~~~88 8b      88`8b   88~~~~~ 88 V8o88 88   88   `Y8b.    88    88~~~88    88    88~~~~~ 
88   8D 88   88 Y8b  d8 88 `88. 88.     88  V888 88  .8D db   8D    88    88   88    88    88.     
Y8888P' YP   YP  `Y88P' YP   YD Y88888P VP   V8P Y8888D' `8888Y'    YP    YP   YP    YP    Y88888P 
'''

@dataclass
class BackendState:
    """
    Configuration for the Backend.
    """
    start_of_week: int = 0  # 0 = Monday, 6 = Sunday
    widget_types: list[type] = NotImplemented  # List of widget types to use
    period_type: type = periods.WeekPeriod  # The type of period to render (e.g., WeekPeriod)

    def __post_init__(self):
        # - Validate start_of_week
        if not (0 <= self.start_of_week <= 6):
            raise ValueError("start_of_week must be between 0 (Monday) and 6 (Sunday)")
        # - Default widget types if not provided
        if self.widget_types is NotImplemented:
            self.widget_types = [widgets.EventDensityWidget, widgets.HolidaysCountWidget, widgets.ExceptionsCountWidget]


'''
d8888b.  .d8b.   .o88b. db   dD d88888b d8b   db d8888b. 
88  `8D d8' `8b d8P  Y8 88 ,8P' 88'     888o  88 88  `8D 
88oooY' 88ooo88 8P      88,8P   88ooooo 88V8o 88 88   88 
88~~~b. 88~~~88 8b      88`8b   88~~~~~ 88 V8o88 88   88 
88   8D 88   88 Y8b  d8 88 `88. 88.     88  V888 88  .8D 
Y8888P' YP   YP  `Y88P' YP   YD Y88888P VP   V8P Y8888D' 
'''

class Backend:
    def __init__(self, period_db: PeriodDB = NotImplemented, state: BackendState = BackendState()) -> None:
        self._period_db = period_db
        self._state = state

    def _generate_labels_html(self, period) -> str:
        """
        Generates the HTML for the week header.
        """
        iso_year, iso_week, _ = period.start_date.isocalendar()
        month_label = period.start_date.strftime('%B')
        return (f'<div class="week-header-labels">'
                f'  <span class="week-label week-label-year">{iso_year}</span>'
                f'  <span class="week-label week-label-month">{month_label}</span>'
                f'  <span class="week-label week-label-separator">–</span>'
                f'  <span class="week-label week-label-weeknum">Week {iso_week:02d}</span>'
                f'</div>')

    def _generate_widgets_html(self, this_period: periods.Period) -> str:
        """
        Generates the HTML for the week widgets.
        """
        html = f'<div class="week-header-widgets">'
        for widget_type in self._state.widget_types:
            widget_instance = widget_type()
            widget_instance: widgets.Widget
            widget_html = widget_instance.render(period_type=self._state.period_type, start_date=this_period.start_date, period_db=self._period_db)
            html += widget_html
        html += '</div>'
        return html
    
    def render_period_html(self, around_date: date) -> str:
        """
        Renders the HTML for a given period type and start date.
        """
        period = self._period_db.get(period_type=self._state.period_type, around_date=around_date)
        labels_html = self._generate_labels_html(period)
        widgets_html = self._generate_widgets_html(period)
        body_html = period.generate_html(widget_types=self._state.widget_types)
        return (f'<div class="week-header">'
                f'  {labels_html}'
                f'  {widgets_html}'
                f'</div>'
                f'<div class="week-body">'
                f'  {body_html}'
                f'</div>')