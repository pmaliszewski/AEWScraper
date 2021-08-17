from typing import List, Set

from constants import Event, Wrestler
from utils import find_same_ids


def _clean_up_wrestler_references(events: List[Event]) -> List[Event]:
    cache: Set[Wrestler] = set()
    for event in events:
        for match in event.matches:
            for wrestler in match.winning_side + match.losing_side:
                cache.add(wrestler)
    for event in events:
        for match in event.matches:
            for side in (match.winning_side, match.losing_side):
                for wrestler in side:
                    for cached_wrestler in side:
                        if wrestler == cached_wrestler:
                            side.remove(wrestler)
                            side.append(cached_wrestler)
    return events


def _sort_by_date(events: List[Event]) -> List[Event]:
    return sorted(events, key=lambda x: x.date)


def _create_id_prompt(wrestler_id: int, values: List[str]) -> str:
    output = f"Choose common name for id: {wrestler_id}\n"
    for index, name in enumerate(values):
        output += f"{index}: {name}\n"
    return output


def _merge_same_ids(events: List[Event]) -> List[Event]:
    same_ids = find_same_ids(events)
    for k, v in same_ids.items():
        sorted_values = sorted(list(v))
        while True:
            try:
                choice = int(input(_create_id_prompt(k, sorted_values)))
                if 0 > choice > len(sorted_values):
                    raise ValueError()
                else:
                    break
            except ValueError:
                print("Please choose a valid index.")
        common_name = sorted_values[choice]
        for event in events:
            for match in event.matches:
                for wrestler in match.winning_side + match.losing_side:
                    if wrestler.wrestler_id == k and wrestler.name != common_name:
                        wrestler.name = common_name
    return events
