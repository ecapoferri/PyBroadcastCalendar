# PyBroadcastCalendar

A quick, shorthand, module to calculate date indices for year, quarter, month,
week and day relative to the [broadcast
calendar](https://en.wikipedia.org/wiki/Broadcast_calendar) with a given
Gregorian calendar date (as dateteime.date). Use of the `BroadcastDate` class (a `dataclasses.dataclass`)
instantiates an object with those indices as `int` properties.

## Example

For 2023-01-21:

- Broadcast calendar year: 2023 (broadcast calendar year 2023  starts on
  2022-12-26)
- Broadcast calendar quarter: 1st
- Broadcast calendar month: February (2)
- Broadcast calendar week: 9
- Broadcast calendar day of the year: 58th
- Broadcast calendar weekday: 2 (Tuesday, based on a Monday - Sunday week)

Broadcast calendar indices for 2023-02-21: year 2023, week 9, day 2.

```python
>>> import datetime
>>> from [bcc_main] | [name_the_module_as_you_like] import BroadcastDate
>>> date_ = datetime.datetime(2023, 2, 21).date()
>>> BroadcastDate(date_)
BroadcastDate(report_date=datetime.date(2023, 2, 21), year_id=2023, qtr_id=1, month_id=2, day_id=58, weekday_id=2, week_id=9)
```
