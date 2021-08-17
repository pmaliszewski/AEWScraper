import glob
import time
from pathlib import Path
from pprint import pprint
from typing import List, Dict, Set

from constants import Event


def be_gentle():
    time.sleep(3)


def create_list_of_events(path: Path) -> List[Event]:
    events = []
    for filepath in glob.iglob(str(path / "*.csv")):
        events.append(Event.create_from_csv(filepath))
    return events


def get_all_wrestlers(path: Path, to_print: bool) -> Dict[str, List[str]]:
    wrestlers = {}
    events = create_list_of_events(path)
    for event in events:
        for match in event.matches:
            for wrestler in match.losing_side + match.winning_side:
                if wrestler.name in wrestlers:
                    wrestlers[wrestler.name].append(event.title)
                else:
                    wrestlers[wrestler.name] = [event.title]
    if to_print:
        pprint(set(wrestlers))
    return wrestlers


def get_single_wrestler(name: str, path: Path) -> List[str]:
    wrestlers = get_all_wrestlers(path, False)
    return wrestlers.get(name, None)


def find_same_ids(events: List[Event]) -> Dict[int, Set[str]]:
    ids_to_name = {}
    for event in events:
        for match in event.matches:
            for wrestler in match.losing_side + match.winning_side:
                if wrestler.participant_id in ids_to_name:
                    ids_to_name[wrestler.participant_id].add(wrestler.name)
                else:
                    ids_to_name[wrestler.participant_id] = {wrestler.name}
    return {k: v for k, v in ids_to_name.items() if len(v) > 1 and k is not None}
