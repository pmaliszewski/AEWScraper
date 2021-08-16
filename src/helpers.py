import glob
from pathlib import Path
from pprint import pprint
from typing import List, Dict

from constants import Event


def get_all_wrestlers(path: Path, to_print: bool) -> Dict[str, List[str]]:
    wrestlers = {}
    for filepath in glob.iglob(str(path / "*.csv")):
        try:
            event = Event.create_from_csv(filepath)
        except:
            print(filepath)
            continue
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


def find_same_ids(path: Path):
    ids_to_name = {}
    for filepath in glob.iglob(str(path / "*.csv")):
        try:
            event = Event.create_from_csv(filepath)
        except:
            print(filepath)
            continue
        for match in event.matches:
            for wrestler in match.losing_side + match.winning_side:
                if wrestler.participant_id in ids_to_name:
                    ids_to_name[wrestler.participant_id].add(wrestler.name)
                else:
                    ids_to_name[wrestler.participant_id] = {wrestler.name}
    for k, v in ids_to_name.items():
        if len(v) > 1:
            print(f"{k}: {v}")


# get_all_wrestlers(Path("C:/Users/Paweł/Desktop/dumps"))
# print(find_same_ids(Path("C:/Users/Paweł/Desktop/dumps")))
