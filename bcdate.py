"""Module supporting the dataclass: BroadcastDate which, taking a
    Date as argument, returns other relative dates and
    broadcast calendar indices.

Raises:
    _DateTableLimitError: Subclass of ValueError Exception. Raised when
        the date supplied to initialize BroadcastDate is outside the
        date range of the calendar table in the data source.
"""
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Generator

from pandas import DataFrame as Df
from pandas import read_csv as pd_read_csv
from pandas import to_datetime as pd_to_datetime
from itertools import chain

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


class _DateTableLimitError(ValueError):
    """If date is outside the range of dates generated DataFrame series
        of month start dates. Thsi should be depricated as the DataFrame
        calculation is now dynamic and relative to the supplied
        self.report_date.
    """


@dataclass
class BroadcastDate:
    """Dataclass: with a datetime.date as argument, returns other relative
        dates and broadcast calendar indices.

    Raises:
        _DateTableLimitError: If date is outside the range of dates
            generated DataFrame series of month start dates. Thsi should
            be depricated as the DataFrame calculation is now dynamic
            and relative to the supplied self.report_date.
    """
    report_date: Date = field(
        init=True, default=datetime.now().date())

    # dates_df: Df
    year_id: int = field(init=False)
    year_start: Date = field(init=False)
    month_id: int = field(init=False)
    month_start: Date = field(init=False)
    year_day_id: int = field(init=False)
    weekday_id: int = field(init=False)
    week_id: int = field(init=False)
    week_start: Date = field(init=False)
    wkday_abbr: str = field(init=False)
    qtr_id: int = field(init=False)
    prev_wk_year_id: int = field(init=False)
    next_wk_year_id: int = field(init=False)
    prev_wk_week_id: int = field(init=False)
    next_wk_week_id: int = field(init=False)
    prev_wk_qtr_id: int = field(init=False)
    next_wk_qtr_id: int = field(init=False)

    def __post_init__(self):
        dates_df = date_df(self.report_date)
        min_date = dates_df.month_start.min() + timedelta(days=7)
        max_date = dates_df.month_start.max()

        if not min_date <= self.report_date <= max_date:
            raise _DateTableLimitError(
                "Date out of range to calculate relative values from existing date table")

        # return year_id_, year_start_, month_id, month_start_
        self.year_id,\
            self.year_start,\
            self.month_id,\
            self.month_start = \
            bc_date_values(self.report_date, dates_df)
        # Day id of the day of the year, aka, 'n' days into the year.
        self.year_day_id = get_year_day_id(self.report_date, self.year_start)

        self.weekday_id = get_weekday_id(self.year_day_id)

        self.week_id = get_week_id(self.year_day_id, self.weekday_id)

        self.week_start = get_week_start(self.report_date, self.weekday_id)

        self.wkday_abbr = WKDAY_ABBRV_MAP[self.weekday_id]

        self.qtr_id = get_qtr_id(self.month_id)

        prev_wk_date, next_wk_date = (
            self.report_date + timedelta(days=diff)
            for diff in (-7, 7)
        )

        self.prev_wk_year_id,\
            prev_wk_yr_start,\
            prev_wk_month_id,\
            _ = \
            bc_date_values(prev_wk_date, dates_df)

        self.next_wk_year_id,\
            next_wk_yr_start,\
            next_wk_month_id,\
            _ = \
            bc_date_values(next_wk_date, dates_df)

        self.prev_wk_week_id,\
            self.next_wk_week_id = (
                get_week_id(
                    year_day_id_=get_year_day_id(prwdate, prwyrst),
                    weekday_id_=get_weekday_id(
                        get_year_day_id(prwdate, prwyrst)),
                )
                for prwdate, prwyrst in (
                    (prev_wk_date, prev_wk_yr_start),
                    (next_wk_date, next_wk_yr_start),
                )
            )

        self.prev_wk_qtr_id,\
            self.next_wk_qtr_id = (
                get_qtr_id(id)
                for id in
                (prev_wk_month_id, next_wk_month_id)
            )


def date_df(date_df_date: Date):
    def _generate_week_start(date__: Date) -> Date:
        year_ = date__.year
        return date__ - timedelta(days=date__.weekday())

    def _generate_month_table(year_: int, month_range: tuple[int, int]
                              ) -> Generator[DateTableRow, None, None]:
        """
        Generate tables for December of the previous, all of the current,
            and January of next year, covering all possible dates
            calculated in BroadcastDate.
        """
        for month_id in range(month_range[0], month_range[1] + 1):
            month_start = _generate_week_start(
                datetime(year_, month_id, 1).date())
            yield {
                'year': year_,
                'month_id': month_id,
                'month_start': month_start,
            }

    def _generate_three_years(year__: int) -> Generator[
            Generator[DateTableRow, None, None], None, None]:
        """
        Generate tables for December of the previous, all of the current,
            and January of next year, covering all possible dates
            calculated in BroadcastDate.
        """
        for yr, mnrng in (
            (year__ - 1, (12, 12)),
            (year__, (1, 12)),
            (year__ + 1, (1, 1))
        ):
            yield _generate_month_table(yr, mnrng)

    return Df(chain(*_generate_three_years(date_df_date.year)))


def bc_date_values(date_: Date, dates_df_: Df,
        ) -> tuple[int, Date, int, Date]:
    """
    Args:
        date_ (date): Supplied date.
        dates_df_ (Df): DataFrame with first days of each month in the
            broadcast calendar, month indices, and broadcast year.

    Returns:
        tuple[
            int: Broadcast year.
            date: First date of the broadcast year.
            int: Broadcast month number (1 - 12).
            date: First date of the broadcast month.
        ]
    """

    # Most recent month start date:
    month_start_: Date = dates_df_.month_start\
                          .loc[dates_df_.month_start.le(date_)]\
                          .max()

    month_id_ = \
                dates_df_.loc[dates_df_.month_start == month_start_]\
                .values[0][1]

    year_id_: int = int(dates_df_.loc[dates_df_.month_start == month_start_]
                        .values[0][0])

    year_start_: Date = dates_df_.month_start\
        .loc[dates_df_.year == year_id_].min()

    return year_id_, year_start_, month_id_, month_start_


def get_qtr_id(month_id_: int):
    """
    Args:
        month_id_ (int): Month number (1 - 12) in the broadcast
            calendar. Generated from date by bc_date_values.

    Returns:
        int: Quarter number (1 - 4) in the broadcast calendar.
    """
    return int((month_id_ - (month_id_ % 3)) / 3 + 1)


def get_year_day_id(report_date_: Date, year_start: Date
        ) -> int:
    """
    Args:
        report_date_ (date): Supplied date.
        year_start (date): First date of the broadcast calendar
            year. Generated by bc_date_values.

    Returns:
        int: Number of the day of the broadcast calendar year
            (1 - 364/371).
    """
    return (report_date_ - year_start + timedelta(days=1)).days


def get_weekday_id(year_day_id_: int) -> int:
    """
    Args:
        year_day_id_ (int): Number of the day of the broadcast calendar
            year (1 - 364/371). Generated from a date by get_year_day_id

    Returns:
        int: Number of the day of the week (Monday 1 - Friday 7).
    """
    return (year_day_id_ - 1) % 7 + 1


def get_week_id(year_day_id_: int, weekday_id_: int) -> int:
    """
    Args:
        year_day_id_ (int): Number of the day of the year (1 - 364/371).
            Generated from a date by get_year_day_id
        weekday_id_ (int): Number of the day of the week
            (Monday 1 - Friday 7). Generated by get_weekday_id.

    Returns:
        int: Week id (1 - 52/53) in the broadcast calendar.
    """
    return int((year_day_id_ - weekday_id_) / 7) + 1


def get_week_start(report_date_: Date, weekday_id_: int
        ) -> Date:
    """
    Args:
        report_date_ (date): Supplied date.
        weekday_id_ (int): Number of the day of the week
            (Monday 1 - Friday 7). Generated by get_weekday_id.

    Returns:
        date: Date of the first day of the broadcast calendar
            week.
    """
    return report_date_ - timedelta(days=weekday_id_ - 1)
