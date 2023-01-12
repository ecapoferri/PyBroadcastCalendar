from datetime import datetime, timedelta
from pandas import to_datetime as pd_to_datetime
from pandas import read_csv as pd_read_csv
from pandas import DataFrame as Df


# Constants
CONF: list[dict[str, str | bool]] = [
    {'col': 'year', 'astype': 'UInt16'},
    {'col': 'month_id', 'astype': 'UInt8'},
    {'col': 'month_start', 'astype': False},
]
WKDAY_ABBRV = {
    1: 'mo',
    2: 'tu',
    3: 'we',
    4: 'th',
    5: 'fr',
    6: 'sa',
    7: 'su',
}

# TODO: CREATE CUSTOM EXCEPTION

def date_df(config: dict = CONF) -> Df:
    # Load table of month start df.
    astype: dict[str, str] = {d['col']: d['astype']
                              for d in config if d['astype']}
    usecols: list[str] = [d['col'] for d in config]
    df = pd_read_csv('dates.csv', encoding='utf-8', usecols=usecols)\
        .convert_dtypes()
    df.month_start = pd_to_datetime(df.month_start).dt.date
    df = df\
        .astype(astype)\
        .sort_values('month_start')
    return df


def bc_date_values(date_bc: datetime.date
                   ) -> dict:
    dates: Df = date_df()
    # This limits the usable dates. If outside this range, the table doesn't
    #   have the data to find values.
    min_date = date_df(CONF).month_start.min()
    max_date = date_df(CONF).month_start.max()

    if not min_date <= date_bc <= max_date:
        raise Exception("Date out of range for existing date table")

    # Most recent month start date:
    month_start: datetime.date = dates.month_start\
        .loc[dates.month_start.
             le(date_bc)]\
        .max()

    year_id: int = int(dates.loc[dates.month_start == month_start]
                       .values[0][0])

    year_start: datetime.date = dates.month_start\
        .loc[dates.year == year_id].min()

    # Day id of the day of the year, aka, 'n' days into the year.
    year_day_id = (date_bc - year_start + timedelta(days=1)).days

    month_id = dates.loc[dates.month_start == month_start]\
        .values[0][1]

    # Mon: 1 - Fri: 7
    weekday_id = (year_day_id - 1) % 7 + 1

    week_start = date_bc - timedelta(days=weekday_id - 1)

    week_id = int((year_day_id - weekday_id) / 7) + 1

    qtr_id = int(
        (month_id - (month_id % 3)) / 3 + 1
    )

    return {
        'year_id': year_id,
        'year_start': year_start,
        'year_day_id': year_day_id,
        'qtr_id': qtr_id,
        'month_start': month_start,
        'month_id': month_id,
        'week_id': week_id,
        'week_start': week_start,
        'weekday_id': weekday_id,
    }


def bc_dates(date_: datetime.date) -> dict:
    # This limits the usable dates. If outside this range, the table doesn't
    #   have the data to find previous and next week values.
    min_date = date_df(CONF).month_start.min() + timedelta(days=7)
    max_date = date_df(CONF).month_start.max()

    if not min_date <= date_ <= max_date:
        raise Exception(
            "Date out of range to calculate relative values from existing date table")

    date_values: dict = bc_date_values(date_)

    prev_wk_values: dict = bc_date_values(
        date_values['week_start'] - timedelta(days=7))

    next_wk_values: dict = bc_date_values(
        date_values['week_start'] + timedelta(days=7))

    return date_values | {
        'prev_wk_week_id': prev_wk_values['week_id'],
        'prev_wk_year_id': prev_wk_values['year_id'],
        'prev_wk_qtr_id': prev_wk_values['qtr_id'],
        'next_wk_week_id': next_wk_values['week_id'],
        'next_wk_year_id': next_wk_values['year_id'],
        'next_wk_qtr_id': next_wk_values['qtr_id'],
    }
