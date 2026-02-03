
from backend import periods

from backend.period_db import PeriodDB
from backend.backend import Backend

def get_backend():
    from backend.backend import Backend
    from backend.period_db import PeriodDB
    return Backend(PeriodDB([]))
