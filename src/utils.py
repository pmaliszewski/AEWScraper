import glob
import time
from pathlib import Path
from typing import List, Dict, Set

from constants import Event, Wrestler


def be_gentle():
    time.sleep(3)


def create_list_of_events(path: Path) -> List[Event]:
    events = []
    for filepath in glob.iglob(str(path / "*.csv")):
        events.append(Event.create_from_csv(filepath))
    return events


def get_all_wrestlers(events: List[Event]) -> Set[Wrestler]:
    wrestlers = set()
    for event in events:
        for match in event.matches:
            for wrestler in match.losing_side + match.winning_side:
                wrestlers.add(wrestler)
    return wrestlers


def find_same_ids(events: List[Event]) -> Dict[int, Set[str]]:
    ids_to_name = {}
    for event in events:
        for match in event.matches:
            for wrestler in match.losing_side + match.winning_side:
                if wrestler.wrestler_id in ids_to_name:
                    ids_to_name[wrestler.wrestler_id].add(wrestler.name)
                else:
                    ids_to_name[wrestler.wrestler_id] = {wrestler.name}
    return {k: v for k, v in ids_to_name.items() if len(v) > 1 and k is not None}
