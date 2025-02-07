import calendar
import time
from datetime import datetime

NOW_DATE = datetime.now()
NOW_TIMESTAMP = int(time.time())
ONE_DAY = 24 * 3600
ONE_WEEK = 7 * ONE_DAY
TIME_RANGES = {
    "LAST_DAY": NOW_TIMESTAMP - ONE_DAY,
    "LAST_WEEK": NOW_TIMESTAMP - ONE_WEEK,
    "LAST_MONTH": NOW_TIMESTAMP
    - calendar.monthrange(NOW_DATE.year, NOW_DATE.month)[1] * ONE_DAY,
    "MTD": NOW_TIMESTAMP - (NOW_DATE.day - 1) * ONE_DAY,
    "LAST_YEAR": NOW_TIMESTAMP - 365 * ONE_DAY,
    "YTD": NOW_TIMESTAMP - (NOW_DATE.timetuple().tm_yday - 1) * ONE_DAY,
    "LAST_5_YEARS": NOW_TIMESTAMP - 5 * 365 * ONE_DAY,
    "ALL": 0,
}
