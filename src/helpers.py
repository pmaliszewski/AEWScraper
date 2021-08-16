import glob
from pathlib import Path
from pprint import pprint

from constants import Event


def get_all_wrestlers(path: Path) -> None:
    wrestlers = {}
    for filepath in glob.iglob(str(path / "*.csv")):
        try:
            event = Event.create_from_csv(filepath)
        except:
            print(filepath)
        for match in event.matches:
            for wrestler in match.losing_side + match.winning_side:
                if wrestler.name in wrestlers:
                    wrestlers[wrestler.name].append(event.title)
                else:
                    wrestlers[wrestler.name] = [event.title]
    pprint(set(wrestlers.keys()))


# get_all_wrestlers(Path("C:/Users/Paweł/Desktop/dumps"))
