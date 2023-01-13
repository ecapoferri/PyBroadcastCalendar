from datetime import datetime, timedelta
from pandas import to_datetime as pd_to_datetime
from pandas import read_csv as pd_read_csv
from pandas import DataFrame as Df
from dataclasses import dataclass, field

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

class DateTableLimitError(ValueError):
    # Used to indicate date outside existing Broadcast Year value range.
    pass


def date_df() -> Df:
    conf: list[dict[str, str | bool]] = [
        {'col': 'year', 'astype': 'UInt16'},
        {'col': 'month_id', 'astype': 'UInt8'},
        {'col': 'month_start', 'astype': False},
    ]
    # Load table of month start df.
    astype: dict[str, str] = {d['col']: d['astype']
                            for d in conf if d['astype']}
    usecols: list[str] = [d['col'] for d in conf]
    df = pd_read_csv('dates.csv', encoding='utf-8', usecols=usecols)\
        .convert_dtypes()
    df.month_start = pd_to_datetime(df.month_start).dt.date
    df = df\
        .astype(astype)\
        .sort_values('month_start')
    return df


def bc_date_values(date_: datetime.date, dates_df_: Df,
        ) -> tuple[int, datetime.date, int, datetime.date]:
    # This limits the usable dates. If outside this range, the table doesn't
    #   have the data to find values.
    # Most recent month start date:
    month_start_: datetime.date = dates_df_.month_start\
        .loc[dates_df_.month_start.
             le(date_)]\
        .max()

    month_id_ = dates_df_.loc[dates_df_.month_start == month_start_]\
        .values[0][1]

    year_id_: int = int(dates_df_.loc[dates_df_.month_start == month_start_]
                        .values[0][0])

    year_start_: datetime.date = dates_df_.month_start\
        .loc[dates_df_.year == year_id_].min()

    return year_id_, year_start_, month_id_, month_start_


def get_qtr_id(month_id_: int):
    return int((month_id_ - (month_id_ % 3)) / 3 + 1)


def get_week_id(year_day_id_: int, weekday_id_: int) -> int:
    return int((year_day_id_ - weekday_id_) / 7) + 1


def get_weekday_id(year_day_id_: int) -> int:
    return (year_day_id_ - 1) % 7 + 1


def get_year_day_id(report_date_: datetime.date, year_start: datetime.date
        ) -> int:
    return (report_date_ - year_start + timedelta(days=1)).days


def get_week_start(report_date_: datetime.date, weekday_id_: int
        ) -> datetime.date:
    return report_date_ - timedelta(days=weekday_id_ - 1)


@dataclass
class BroadcastDate:

    report_date: datetime.date = field(
        init=True, default=datetime.now().date())

    year_id: int = field(init=False)
    year_start: datetime.date = field(init=False)
    month_id: int = field(init=False)
    month_start: datetime.date = field(init=False)
    year_day_id: int = field(init=False)
    weekday_id: int = field(init=False)
    week_id: int = field(init=False)
    week_start: datetime.date = field(init=False)
    wkday_abbr: str = field(init=False)
    qtr_id: int = field(init=False)
    prev_wk_year_id: int = field(init=False)
    next_wk_year_id: int = field(init=False)
    prev_wk_week_id: int = field(init=False)
    next_wk_week_id: int = field(init=False)
    prev_wk_qtr_id: int = field(init=False)
    next_wk_qtr_id: int = field(init=False)

    def __post_init__(self):
        dates_df: Df = date_df()

        min_date = date_df().month_start.min() + timedelta(days=7)
        max_date = date_df().month_start.max()

        if not min_date <= self.report_date <= max_date:
            raise DateTableLimitError(
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
        
        self.prev_wk_week_id = get_week_id(
            year_day_id_=get_year_day_id(prev_wk_date, prev_wk_yr_start),
            weekday_id_=get_weekday_id(
                get_year_day_id(prev_wk_date, prev_wk_yr_start))
        )

        self.next_wk_week_id = get_week_id(
            year_day_id_=get_year_day_id(next_wk_date, next_wk_yr_start),
            weekday_id_=get_weekday_id(
                get_year_day_id(next_wk_date, next_wk_yr_start))
        )

        self.prev_wk_qtr_id,\
        self.next_wk_qtr_id = (get_qtr_id(id) for id in
            (prev_wk_month_id, next_wk_month_id)
        )

if __name__ == "__main__":
    pass
