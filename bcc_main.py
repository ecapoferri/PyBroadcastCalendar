"""Module supporting the dataclass: BroadcastDate which, taking a
    datetime.date as argument, returns other relative dates and
    broadcast calendar indices. Functions are available for input.
    Requires python>=3.10."""
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Annotated, Generator, Optional

MAX_MONTHS = 12
DAYS_IN_A_WEEK = 7

_Date = Annotated[date, 'datetime.date']

logging.basicConfig(format='[%(levelname)s] %(message)s')

class BroadcastCalendarValErr(ValueError):
    """Essentially an alias for ValueError. The input values for (year_)
        and (month_range) are validated for type and realistic range."""


@dataclass
class BroadcastDate:
    """Dataclass: with a datetime.date as argument, returns other
        relative dates and broadcast calendar indices."""
    report_date: _Date = field(init=True, default=datetime.now().date(),)

    year_id: int = field(init=False,)
    qtr_id: int = field(init=False,)
    month_id: int = field(init=False,)
    day_id: int = field(init=False,)
    weekday_id: int = field(init=False,)
    week_id: int = field(init=False,)

    def __post_init__(self,):
        self.year_id,\
        self.qtr_id,\
        self.month_id,\
        self.week_id,\
        self.day_id \
        = bcweek_values(self.report_date,)

        self.weekday_id = self.report_date.weekday() + 1


def week_dates_array(monday_date: _Date,) -> Generator[_Date, None, None]:
    """Given a Monday date, yield 7 days of dates for the week."""
    for wkd in range(DAYS_IN_A_WEEK):
        yield monday_date + timedelta(days=wkd)


def week_start(date_: _Date,) -> _Date:
    """Returns the date of the Monday of the week containing the give
        date."""
    return (date_ - timedelta(days=date_.weekday()))


def calc_year_month_ids(date_: _Date,) -> tuple[int, int, _Date]:
    """Returns a broadcast week id given a date for the start of the
        week. Also returns the start date of the broadcast week.

    Args:
        date_ (_Date): A normal Gregorian Calendar data as a
            datetime.date.

    Returns:
        tuple[int, int, _Date]:
            (int): Year ID of the broadcast calendar year.
            (int): Month ID of the broadcast calendar month.
            (_Date): Gregorian caldendar date (as datetime.date) of the
                day of the broadcast calendar week.
    """
    week_start_ = week_start(date_)
    # Determine the mininum day of the month within the current week.
    week_dates: list[_Date] = list(week_dates_array(week_start_,))
    week_dates.sort(key=lambda x: x.day)
    min_month_day_ = week_dates[0]

    # year_id, month_id, week_start
    return min_month_day_.year, min_month_day_.month, week_start_


def calc_week_id(year_id_: int, monday_date: _Date,) -> tuple[int, _Date]:
    """Returns a broadcast week id given a date for the start of the
        week. Also returns the start date of the broadcast week.

    Args:
        year_id_ (int): Year ID of the broadcast calendar year.
        monday_date (_Date): Gregorian caldendar date (as datetime.date)
            of the day of the broadcast calendar week.

    Returns:
        tuple[int, _Date]:
            (int): Gregorian caldendar date (as datetime.date) of the
                day of the broadcast calendar year.
            (_Date): datetime.date of the Monday at the beginning of the
                broadcast calendar year.
    """
    year_jan_first = date(year=year_id_, month=1, day=1,)
    # Gets the first day of the broadcast year with the given date.
    _, _, year_start_monday = calc_year_month_ids(year_jan_first,)
    return \
        int((monday_date - year_start_monday).days / DAYS_IN_A_WEEK + 1),\
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


def _max_week_id(year_id_: int) -> int:
    next_bc_year_start = week_start(date(year_id_ + 1, 1, 1))
    max_week_id = BroadcastDate(next_bc_year_start - timedelta(days=1)).week_id
    return max_week_id


def reverse_broadcastdate(year_id: int, week_id: Optional[int] = None,
                          month_id: Optional[int] = None,
                          suppress_warnings: bool = False,
                          ) -> _Date:  # type: ignore
    """
    Calculate a date for the start of a broadcast year or broadcast
        week.

    Args:
        year_id (int): Year ID of a broadcast calendar year.
        week_id (Optional[int], optional): Week ID of a broadcast
            calendar year.
            Defaults to None.
        month_id (Optional[int], optional): Month ID of a broadcast
            calendar year. If a week ID is also supplied, this will be
            ignored and a warning message will be emitted.
            Defaults to None.
        suppress_warnings (bool, optional): If set to True, will
            suppress the ignore month_id warning.
            Defaults to False.

    Raises:
        BroadcastCalendarValErr: The function checks the validity of the
            supplied arguments for month_id and/or week_id.

    Returns:
        _Date (datetime.date): If a week_id is supplied, it will be the
            Gregorian calendar date of the start of that broadcast
            calendar week. If no week_id is supplied, but month_id is
            supplied, it will be the Gregorian calendar date of the
            start of that broadcast calendar month. If neither are
            supplied, it will be the date of the start of the broadcast
            calendar year.
    """
    broadcast_year_start = week_start(date(year_id, 1, 1))
    # Return the start of the broadcast calendar year if no other args are
    #   supplied.
    if not any([week_id, month_id]):
        return broadcast_year_start

    # If a valid week number is supplied, return the start of that week.
    if week_id:
        if month_id and not suppress_warnings:
            warning_msg = f"{week_id=} was supplied. Ignoring {month_id=}"
            logging.warning(warning_msg)

        max_week_id = _max_week_id(year_id)

        if week_id > max_week_id:
            err_msg = \
                f"reverse_broadcastdate: {week_id=} was supplied. Broadcast " \
                + f"calendar year {year_id} only has {max_week_id} weeks"
            raise BroadcastCalendarValErr(err_msg)

        return broadcast_year_start + timedelta(weeks=week_id - 1)

    # If a valid month is supplied, return the start of that month.
    if month_id:
        if not 1 <= month_id <= MAX_MONTHS:
            err_msg = \
                f"Theres only {MAX_MONTHS} in a year. {month_id=} was supplied"
            raise BroadcastCalendarValErr(err_msg)

        return week_start(date(year_id, month_id, 1))
