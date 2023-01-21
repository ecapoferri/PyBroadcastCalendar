"""Module supporting the dataclass: BroadcastDate which, taking a
    datetime.date as argument, returns other relative dates and
    broadcast calendar indices. Functions are available for input."""
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Annotated, Generator

_Date = Annotated[date, 'datetime.date']
_MonthRange = Annotated[tuple[int, int], 'tuple[int, int]']

_DateTableRow = Annotated[dict[str, int | _Date],
    r'_DateTableRow{int: Year, int: MonthID, datetime.date: MonthStart}',
]

# Constants

# Expected year values are used to validate input values.
MIN_YEAR = 1900
MAX_YEAR = 2400

WKDAY_ABBRV_MAP = [
    'mo',
    'tu',
    'we',
    'th',
    'fr',
    'sa',
    'su',
]


class BroadcastCalendarValErr(ValueError):
    """Essentially an alias for ValueError. The input values for (year_)
        and (month_range) are validated for type and range."""


@dataclass
class BroadcastDate:
    """Dataclass: with a datetime.date as argument, returns other relative
        dates and broadcast calendar indices.
    """
    report_date: _Date = field(init=True, default=datetime.now().date(),)

    # dates_df: Df
    year_id: int = field(init=False,)
    qtr_id: int = field(init=False,)
    month_id: int = field(init=False,)
    day_id: int = field(init=False,)
    weekday_id: int = field(init=False,)
    week_id: int = field(init=False,)
    wkday_abbr: str = field(init=False,)
    prevwk_year_id: int = field(init=False,)
    prevwk_qtr_id: int = field(init=False,)
    prevwk_week_id: int = field(init=False,)
    nextwk_year_id: int = field(init=False,)
    nextwk_qtr_id: int = field(init=False,)
    nextwk_week_id: int = field(init=False,)

    def __post_init__(self,):
        self.year_id,\
        self.qtr_id,\
        self.month_id,\
        self.week_id,\
        self.day_id = \
            bcweek_values(self.report_date,)

        self.weekday_id = self.report_date.weekday() + 1

        self.wkday_abbr = WKDAY_ABBRV_MAP[self.weekday_id - 1]

        self.prevwk_year_id,\
        self.prevwk_qtr_id, _,\
        self.prevwk_week_id, _ = \
            bcweek_values(self.report_date - timedelta(days=7),)

        self.nextwk_year_id,\
        self.nextwk_qtr_id, _,\
        self.nextwk_week_id, _ = \
            bcweek_values(self.report_date + timedelta(days=7),)


def week_dates_array(monday_date: _Date,) -> Generator[_Date, None, None]:
    """Given a Monday date, yield 7 days of dates for the week."""
    for wkd in range(7):
        yield monday_date + timedelta(days=wkd)


def calc_year_month_ids(date_: _Date,) -> tuple[int, int, _Date]:
    """TODO: DOCSTRING"""
    # _Date of Monday of the week.
    week_start_ = (date_ - timedelta(days=date_.weekday()))
    # Determine the mininum day of the month within the current week.
    week_dates: list[_Date] = list(week_dates_array(week_start_,))
    week_dates.sort(key=lambda x: x.day)
    min_month_day_ = week_dates[0]

    # year_id, month_id, week_start
    return min_month_day_.year, min_month_day_.month, week_start_


def calc_week_id(year_id_: int, monday_date: _Date,) -> tuple[int, _Date]:
    """Returns a broadcast week id given a date for the start of the
        week. Also returns the start date of the broadcast week."""
    year_jan_first = datetime(year=year_id_, month=1, day=1,).date()
    # Gets the first day of the broadcast year with the given date.
    _, _, year_start_monday = calc_year_month_ids(year_jan_first,)
    return \
        int((monday_date - year_start_monday).days / 7 + 1),\
        year_start_monday


def bcweek_values(date_: _Date) -> tuple[int, int, int, int, int]:
    """Returns broadcast calendar indices for a given date:
        Year, Quarter, Month, Week, Day of year."""
    year_id_: int
    month_id_: int
    week_start_: _Date
    year_id_, month_id_, week_start_ = \
        calc_year_month_ids(date_=date_,)

    week_id_: int
    year_start_: _Date
    week_id_, year_start_ = calc_week_id(year_id_=year_id_,
                                         monday_date=week_start_,)
    qtr_i_, _ = divmod(month_id_, 4,)
    qtr_id_: int = int(qtr_i_) + 1
    day_id_: int = (date_ - year_start_).days + 1
    return year_id_, qtr_id_, month_id_, week_id_, day_id_


# def calc_week_start(date__: _Date,) -> _Date:
#     """Given a datetime.date (date__) returns the date of the Monday
#         start of that broadcast week.
#     """
#     return date__ - timedelta(days=date__.weekday(),)


def gen_date_table_broadcast_year(
        year_: int, month_range: _MonthRange,
            ) -> Generator[_DateTableRow, None, None]:
    """Generate rows with dates and integer index ids for desired
        broadcast calendar months of a desired broadcast calendar year.

    Args:
        year_ (int): The year id, aka, the year (e.g. 2023) desired.
        month_range (tuple[int, int]): First and last month index ids
            (1 - 12) to be included in the table.

    Raises:
        BroadcastCalendarValErr: Essentially an alias for ValueError.
            The input values for (year_) and (month_range) are validated
            for type and range.

    Yields:
        Generator[DateTableRow, None, None]: When executed, returns

    Examples:
    ---------
    Generate tables for December of the previous, all of the current,
        and January of next year, covering all possible dates
        calculated in BroadcastDate.

    import itertools
    import pandas
    from typing import Generator

    def _date_df(any_date: Date):
        def _generate_three_years(year__: int) -> Generator[
                Generator[DateTableRow, None, None], None, None]:
            for yr_, mnth_rng in (
                (year__ - 1, (12, 12)),
                (year__, (1, 12)),
                (year__ + 1, (1, 1))
            ):
                yield gen_date_table_broadcast_year(yr_, mnth_rng,)

        return pandas.DataFrame(
                                itertools.chain(
                                    *_generate_three_years(any_date.year)))
    """

    # Value Checks
    val_err_mn = ValueError(
        'Month range (month_range) must be a tuple f integers for the first '
        + 'month ID and the last month ID.'
    )
    val_err_yr = ValueError(
        'Year ID (year_) should be an integer representing a valid year number.'
    )
    if not isinstance(month_range, tuple) or len(month_range)==2:
        raise val_err_mn
    for mnidx in month_range:  # type: ignore
        if not isinstance(mnidx, int):
            raise val_err_mn
        if not 1 <= mnidx <= 12:
            raise val_err_mn
    if not isinstance(year_, int):
        raise val_err_yr
    if not MIN_YEAR < year_ < MAX_YEAR:
        raise val_err_yr

    for month_id in range(month_range[0], month_range[1] + 1,):
        _date = datetime(year_, month_id, 1,).date()  # Calendar month start
        # The broadcast month starts on the Monday of the broadcast week (M - U)
        #   containing the first day of the calendar month.
        month_start = _date - timedelta(days=_date.weekday(),)
        
        yield {
            'year': year_,
            'month_id': month_id,
            'month_start': month_start,
        }
