"""
Library for contraint-propagation-based scheduling.

Schedules are made up of Items which are scheduled into one or more
Slots and each have one or more Participants.

We find schedules where all the items are put into Slots such that no
Slot contains more than one item for any Participant.

Slots are somewhat abstract--they could be specific times on an actual
calendar or a more abstract notion (e.g. 60 minutes every Monday at
9am.) Or they could include other dimensions, e.g. a room. (Rooms
could also be modeled as Participants as they often are in calendaring
systems.)

Items have criteria that constrain when they can be scheduled. This
may be as simple as the duration--any free time will do. Or there
could be other constraints such as happening on a certain day of the
week or before a certain time.

Participants can also have constraints which further constrain when a
meeting can be. For instance, if each Participant has a set of working
hours, then a meeting can only be scheduled in the intersection of all
the participants working hours. And Participants can only be scheduled
in one Item per Slot.
"""

import dataclasses
from dataclasses import dataclass
from typing import Callable, Iterator, List, Optional, Set

Predicate = Callable[["Slot"], bool]


@dataclass(frozen=True)
class Slot:
    """
    A time that a thing can be scheduled. Items with overlapping
    participants cannot be scheduled in slots that overlap.
    """

    def overlaps(self, other: "Slot") -> bool:
        "Does this slot overlap with the other slot."
        return self == other


@dataclass(frozen=True)
class Participant:
    """
    A meeting participant. May have constraints about when Items in
    which they are participants can be scheduled.
    """

    name: str

    def slot_ok(self, slot: Slot) -> bool:
        "The given slot is okay for this participant."
        return True


@dataclass
class Item:
    "A thing to be scheduled."

    name: str
    participants: Set[Participant]
    slots: Set[Slot]

    def copy(self):
        return dataclasses.replace(self)

    def remove_slots(self, fn: Predicate) -> bool:
        new = {s for s in self.slots if not fn(s)}
        if len(new) < len(self.slots):
            self.slots = new
            return True
        else:
            return False

    def slot_ok_(self, slot: Slot) -> bool:
        """
        Can this item, in principle, be scheduled in the given slot. Can
        be implemented by subclasses to implement other criteria but
        they should probably call this super class method and and the
        result with their own criteria.
        """
        return all(p.slot_ok(slot) for p in self.participants)

    def impossible(self) -> bool:
        return len(self.slots) == 0

    def scheduled(self) -> bool:
        return len(self.slots) == 1

    def unscheduled(self) -> bool:
        return len(self.slots) > 1

    def overlapping_participants(self, other: "Item") -> bool:
        return bool(self.participants & other.participants)

    def __str__(self):
        ps = [p.name for p in self.participants]
        slot = list(self.slots)[0]
        return f"{self.name} ({', '.join(sorted(ps))}): slot: {slot}"


def schedules(items: List[Item]) -> Iterator[List[Item]]:
    "Iterator of filled in schedules."

    unscheduled = [i for i, item in enumerate(items) if item.unscheduled()]
    if unscheduled:
        for idx in sorted(unscheduled, key=lambda i: len(items[i].slots)):
            for slot in items[idx].slots:
                assigned = assign(items, idx, slot)
                if assigned:
                    yield from schedules(assigned)
    else:
        yield items


def assign(items: List[Item], idx: int, s: Slot) -> Optional[List[Item]]:
    "Assign the item at idx to Slot s and propagate the consequences."
    return eliminate([item.copy() for item in items], idx, lambda x: x != s)


def eliminate(items: List[Item], idx: int, fn: Predicate) -> Optional[List[Item]]:
    "Eliminate slots from item at idx and propagate consequences. Mutates the items."

    item = items[idx]

    if item.remove_slots(fn):

        if item.impossible():
            return None

        elif item.scheduled():
            s = list(item.slots)[0]
            for idx2, item2 in enumerate(items):
                if idx != idx2 and item.overlapping_participants(item2):
                    if not eliminate(items, idx2, s.overlaps):
                        return None

    return items


if __name__ == "__main__":

    @dataclass(frozen=True)
    class SimpleSlot(Slot):

        name: str

        def __str__(self):
            return self.name

    all_slots = {SimpleSlot(c) for c in "123"}

    def item(s):
        return Item(s, {Participant(c) for c in s}, set(all_slots))

    items = [item(s) for s in ("abc", "def", "ace", "ghi", "cdg", "beh")]

    i = 0
    for s in schedules(items):
        print(i)
        for item in items:
            print(item)
        print()
        i += 1

    if i == 0:
        print("no schedules!")
