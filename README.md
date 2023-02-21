# PyBroadcastCalendar

A quick, shorthand, module to calculate date indices for year, quarter, month,
week and day relative to the [broadcast
calendar](https://en.wikipedia.org/wiki/Broadcast_calendar) with a given
Gregorian calendar date (as dateteime.date).

Use of the `BroadcastDate` class (a
`dataclasses.dataclass`) instantiates an object with those indices as `int`
properties.

The function `reverse_broadcastdate` will supply start dates for broadcast
calendar periods (broadcast year, week, or month).

## Examples

### `BroadcastDate(datetime.date)`

#### Example date: 2023-02-21

```python
>>> import date
>>> from [bcc_main] | [name_the_module_as_you_like] import BroadcastDate

>>> date_ = date(2023, 2, 21)
>>> BroadcastDate(date_)

BroadcastDate(report_date=datetime.date(2023, 2, 21), year_id=2023, qtr_id=1, month_id=2, day_id=58, weekday_id=2, week_id=9)
```

- Broadcast calendar year: 2023 (broadcast calendar year 2023  starts on
  2022-12-26)
- Broadcast calendar quarter: 1st
- Broadcast calendar month: February (2)
- Broadcast calendar week: 9
- Broadcast calendar day of the year: 58th
- Broadcast calendar weekday: 2 (Tuesday, based on a Monday - Sunday week)

Broadcast calendar indices for 2023-02-21: year 2023, week 9, day 2.

### `reverse_broadcastdate()`

#### Example: Broadcast Year 2022 (starts on 2021-12-27)

```python
>>> from [bcc_main] | [name_the_module_as_you_like] import reverse_broadcastdate

>>> reverse_broadcastdate(2022)
datetime.date(2021, 12, 27)
```

#### Example: Broadcast Calendar Year 2019, Week 30

```python
>>> from [bcc_main] | [name_the_module_as_you_like] import reverse_broadcastdate

>>> reverse_broadcastdate(2019, 30)
datetime.date(2019, 7, 22)
```

#### Example: Broadcast Calendar May 2020

```python
>>> from [bcc_main] | [name_the_module_as_you_like] import reverse_broadcastdate

>>> reverse_broadcastdate(2020, month_id=5)

datetime.date(2020, 4, 27)
```

#### Supplying both week_id and month_id

```python
>>> from [bcc_main] | [name_the_module_as_you_like] import reverse_broadcastdate

>>> reverse_broadcastdate(2022, 50, 12)

[WARNING] week_id=50 was supplied. Ignoring month_id=12
datetime.date(2022, 12, 5)
```
