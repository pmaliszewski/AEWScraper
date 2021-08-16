import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

CAGEMATCH_SITE = "https://www.cagematch.net"
LIST_OF_EVENTS_SITE = CAGEMATCH_SITE + "/?id=8&nr=2287&page=4&s={paging_id}"

NAME_PREFIX = "Name of the event:"
DATE_PREFIX = "Broadcast date:"


class UnknownMatchError(ValueError):
    pass


@dataclass
class Participant:
    name: str
    participant_id: Optional[int] = None

    def __str__(self) -> str:
        return f"{self.name}:{self.participant_id}"


@dataclass
class Match:
    stipulation: str
    winning_side: Optional[List[Participant]]
    losing_side: Optional[List[Participant]]
    draw: bool = False

    def __str__(self) -> str:
        return (
            f"{self.stipulation};"
            f'{",".join(str(participant) for participant in self.winning_side)};'
            f'{",".join(str(participant) for participant in self.losing_side)};'
            f"{str(self.draw)}"
        )


@dataclass
class Event:
    title: str
    date: datetime.datetime
    matches: List[Match]

    def save_to_csv(self, path: Path) -> None:
        with open(path / f"{self.title}.csv", "w+") as f:
            f.write(self.title + "\n")
            f.write(str(self.date) + "\n")
            for match in self.matches:
                f.write(str(match) + "\n")

    @classmethod
    def create_from_csv(cls, path: Path) -> "Event":
        def _split_participants(side: str) -> List[Participant]:
            output = []
            for wrestler in side.split(","):
                wrestler_info = wrestler.split(":")
                if wrestler_info[1] == "None":
                    participant_id = None
                else:
                    participant_id = int(wrestler_info[1])
                output.append(
                    Participant(name=wrestler_info[0], participant_id=participant_id)
                )
            return output

        title, date, matches = None, None, []
        with open(path) as f:
            for index, line in enumerate(f):
                if index == 0:
                    title = line.rstrip()
                elif index == 1:
                    date = datetime.datetime.strptime(
                        line.rstrip(), "%Y-%m-%d %H:%M:%S"
                    )
                else:
                    info = line.split(";")
                    stipulation = info[0]
                    draw = info[3] == "True"
                    winning_side = _split_participants(info[1])
                    losing_side = _split_participants(info[2])
                    matches.append(
                        Match(
                            stipulation=stipulation,
                            winning_side=winning_side,
                            losing_side=losing_side,
                            draw=draw,
                        )
                    )
        return Event(title=title, date=date, matches=matches)
