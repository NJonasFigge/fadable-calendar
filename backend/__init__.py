
from backend import periods
from backend.period_db import PeriodDB
from backend.backend import Backend

def get_backend():
    from pathlib import Path
    ics_dir = Path(__file__).parent.parent / "data"
    period_db = PeriodDB()
    period_db.load_ical_files(ics_dir.glob("*.ics"))
    return Backend(period_db=period_db)