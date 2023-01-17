"""Module supporting the dataclass: BroadcastDate which, taking a
    Date as argument, returns other relative dates and
    broadcast calendar indices. Functions are available for input."""
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Annotated, Generator

Date = Annotated[date, 'datetime.date']

DateTableRow = Annotated[
    dict[str, int | Date],
    'DateTableRow(Year,MonthID,MonthStart'
]

# Constants
WKDAY_ABBRV_MAP = {
    1: 'mo',
    2: 'tu',
    3: 'we',
    4: 'th',
    5: 'fr',
    6: 'sa',
    7: 'su',
}


@dataclass
class BroadcastDate:
    """Dataclass: with a datetime.date as argument, returns other relative
        dates and broadcast calendar indices.
    """
    report_date: Date = field(init=True, default=datetime.now().date())

    # dates_df: Df
    year_id: int = field(init=False)
    qtr_id: int = field(init=False)
    month_id: int = field(init=False)
    day_id: int = field(init=False)
    weekday_id: int = field(init=False)
    week_id: int = field(init=False)
    wkday_abbr: str = field(init=False)
    prevwk_year_id: int = field(init=False)
    prevwk_qtr_id: int = field(init=False)
    prevwk_week_id: int = field(init=False)
    nextwk_year_id: int = field(init=False)
    nextwk_qtr_id: int = field(init=False)
    nextwk_week_id: int = field(init=False)

    def __post_init__(self):
        # return year_id_, year_start_, month_id, month_start_
        self.year_id,\
        self.qtr_id,\
        self.month_id,\
        self.week_id,\
        self.day_id = \
            bcweek_values(self.report_date)

        self.weekday_id = self.report_date.weekday() + 1

        self.wkday_abbr = WKDAY_ABBRV_MAP[self.weekday_id]

        self.prevwk_year_id,\
        self.prevwk_qtr_id, _,\
        self.prevwk_week_id, _ = \
            bcweek_values(self.report_date - timedelta(days=7))

        self.nextwk_year_id,\
        self.nextwk_qtr_id, _,\
        self.nextwk_week_id, _ = \
            bcweek_values(self.report_date + timedelta(days=7))


def week_dates_array(monday_date: Date) -> Generator[Date, None, None]:
    """Given a Monday date, yield 7 days of dates for the week."""
    for wkd in range(7):
        yield monday_date + timedelta(days=wkd)


def calc_year_month_ids(date_: Date) -> tuple[int, int, Date]:
    """TODO: DOCSTRING"""
    # Date of Monday of the week.
    week_start_ = (date_ - timedelta(days=date_.weekday()))
    # Determine the mininum day of the month within the current week.
    week_dates: list[Date] = list(week_dates_array(week_start_))
    week_dates.sort(key=lambda x: x.day)
    min_month_day_ = week_dates[0]

    # year_id, month_id, week_start
    return min_month_day_.year, min_month_day_.month, week_start_


def calc_week_id(year_id_: int, monday_date: Date) -> tuple[int, Date]:
    """Returns a broadcast week id given a date for the start of the
        week. Also returns the start date of the broadcast week."""
    year_jan_first = datetime(year=year_id_, month=1, day=1).date()
    # Gets the first day of the broadcast year with the given date.
    _, _, year_start_monday = calc_year_month_ids(year_jan_first)
    return \
        int((monday_date - year_start_monday).days / 7 + 1),\
        year_start_monday


def bcweek_values(date_: Date) -> tuple[int, int, int, int, int]:
    """Returns broadcast calendar indices for a given date:
        Year, Quarter, Month, Week, Day of year."""
    year_id_: int
    month_id_: int
    week_start_: Date
    year_id_, month_id_, week_start_ = \
        calc_year_month_ids(date_=date_)

    week_id_: int
    year_start_: Date
    week_id_, year_start_ = calc_week_id(year_id_=year_id_,
                                         monday_date=week_start_,)
    qtr_i_, _ = divmod(month_id_, 4)
    qtr_id_: int = int(qtr_i_) + 1
    day_id_: int = (date_ - year_start_).days + 1
    return year_id_, qtr_id_, month_id_, week_id_, day_id_
