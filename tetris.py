#!/usr/bin/env python3

"""
Create a schedule of recurring meetings attempting to maximize
remaining free time on everyone's calendar. Doesn't look at the
current state of anyone's calendar since that's assumed to be a mess.
"""

from collections import defaultdict
from dataclasses import dataclass
from enum import IntEnum, auto
from math import gcd
from typing import Iterator, Set, Tuple

from scheduling import Slot

Hour = int
Minute = int
Minutes = int
Week = int


class Day(IntEnum):
    "Day of the work week."

    MONDAY = auto()
    TUESDAY = auto()
    WEDNESDAY = auto()
    THURSDAY = auto()
    FRIDAY = auto()


DaysAndWeeks = Set[Tuple[Day, Week]]


@dataclass
class TimeSlot(Slot):
    """
    A slot on an abstract calendar that occurs at a particular time on
    a particular day of our n-week celandar. If we have, say, a six
    week calendar (because some meetings recur on a six week cycle)
    then a slot for a meeting that occurs daily will have days set to
    the cross product of the five days and the six weeks.
    """

    hour: Hour
    minute: Minute
    duration: Minutes
    days: DaysAndWeeks

    def overlaps(self, other: Slot) -> bool:
        if isinstance(other, self.__class__):
            return bool(self.time_overlaps(other) and self.days & other.days)
        else:
            raise Exception("Can only compare slots of the same type")

    def time_overlaps(self, other: "TimeSlot") -> bool:
        self_start, self_end = self.interval()
        other_start, other_end = other.interval()
        return not (self_end <= other_start or self_start >= other_end)

    def interval(self):
        start = (self.hour * 60) + self.minute
        return start, start + self.duration

    def __str__(self):
        days = defaultdict(set)
        for d, w in sorted(self.days):
            days[d].add(w)
        x = "; ".join(f"{d.name} {weeks_desc(days[d])}" for d in days)
        return f"{self.hour:02d}:{self.minute:02d} ({self.duration} minutes) {x}"

    def priority(self) -> int:
        return self.duration * len(self.days)


def weeks_desc(weeks):
    if weeks == set(range(6)):
        return "every week"
    else:
        return f"weeks {','.join(str(w) for w in weeks)}"


class Cadence:
    """
    Generate the sets of possible days and weeks a meeting could occur
    to satisfy a particular cadence. We pass in the number of weeks of
    the total schedule (which should be the LCM of all the weekly
    cadences we are trying to schedule.)
    """

    def days_and_weeks(self, weeks: int) -> Iterator[DaysAndWeeks]:
        pass


@dataclass
class DailyCadence(Cadence):
    "A meeting that occurs every day at the same time."

    def days_and_weeks(self, weeks) -> Iterator[DaysAndWeeks]:
        "There's only one way to schedule a daily meeting: every day."
        yield {(d, w) for d in Day for w in range(weeks)}


@dataclass
class WeeklyCadence(Cadence):
    "A meeting that occurs every n weeks."
    cadence: int = 1

    def days_and_weeks(self, weeks) -> Iterator[DaysAndWeeks]:
        """
        A weekly meeting can be scheduled on any day of the week at a
        number of offsets.
        """
        assert weeks % self.cadence == 0

        for offset in range(self.cadence):
            for d in Day:
                yield {(d, w + offset) for w in range(0, weeks, self.cadence)}


@dataclass
class SpecificWeeklyCadence(Cadence):
    "A meeting that occurs every n weeks on a specific days."
    cadence: int
    days: Set[Day]

    def days_and_weeks(self, weeks) -> Iterator[DaysAndWeeks]:
        assert weeks % self.cadence == 0

        for offset in range(self.cadence):
            yield {
                (d, w + offset)
                for d in self.days
                for w in range(0, weeks, self.cadence)
            }


@dataclass
class SprintCadence(Cadence):
    "A meeting that occurs on a specific day and week (first or second) in the sprint."
    day: Day
    week: int

    def days_and_weeks(self, weeks) -> Iterator[DaysAndWeeks]:
        assert weeks % 2 == 0
        assert self.week in {0, 1}

        yield {(self.day, w + self.week) for w in range(0, weeks, 2)}


@dataclass
class DailyMinusSprintDaysCadence(Cadence):
    "A meeting that occurs daily except a specific day and week (first or second) in the sprint."
    days: DaysAndWeeks

    def days_and_weeks(self, weeks) -> Iterator[DaysAndWeeks]:
        assert weeks % 2 == 0
        daily = {(d, w) for d in Day for w in range(weeks)}
        excluded = {(d, w + sw) for (d, sw) in self.days for w in range(0, weeks, 2)}
        yield daily - excluded


@dataclass
class TimeConstraint:
    """
    Constrain the time a meeting can be. Default implementation
    requires the meeting be exactly at a specific time.
    """

    hour: Hour
    minute: Minute

    def slot_ok(self, slot: TimeSlot) -> bool:
        return self.hour == slot.hour and self.minute == slot.minute


class AtOrBeforeTimeConstraint(TimeConstraint):
    "Require that a meeting start at or before a given time."

    def slot_ok(self, slot: TimeSlot) -> bool:
        return (slot.hour * 60) + slot.minute <= (self.hour * 60) + self.minute


class AtOrAfterTimeConstraint(TimeConstraint):
    "Require that a meeting start at or after a given time."

    def slot_ok(self, slot: TimeSlot) -> bool:
        return (slot.hour * 60) + slot.minute >= (self.hour * 60) + self.minute


class NullTimeConstraint(TimeConstraint):
    def slot_ok(self, slot: TimeSlot) -> bool:
        return True


@dataclass
class MeetingSpec:

    cadence: Cadence
    duration: Minutes
    time_constraint: TimeConstraint

    def possible_slots(self, start_hour=12, end_hour=17, increment=30, total_weeks=6):
        time_constraint = self.time_constraint or NullTimeConstraint(0, 0)
        day_end = end_hour * 60
        for h in range(start_hour, end_hour):
            for m in range(0, 60, increment):
                for days in self.cadence.days_and_weeks(total_weeks):
                    slot = TimeSlot(h, m, self.duration, days)
                    if slot.interval()[1] <= day_end:
                        if time_constraint.slot_ok(slot):
                            yield slot


def lcm(a: int, b: int) -> int:
    "Compute lowest common multipler."
    return int((a * b) / gcd(a, b))
