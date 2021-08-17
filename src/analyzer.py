from typing import List

from constants import Event
from utils import find_same_ids


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
                    if wrestler.participant_id == k and wrestler.name != common_name:
                        wrestler.name = common_name
    return events


# pprint(find_same_ids(_merge_same_ids(create_list_of_events(Path("C:/Users/Paweł/Desktop/dumps")))))
