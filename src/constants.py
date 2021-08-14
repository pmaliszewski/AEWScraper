import datetime
from dataclasses import dataclass
from typing import List, Optional

CAGEMATCH_SITE = "https://www.cagematch.net"
LIST_OF_EVENTS_SITE = CAGEMATCH_SITE + "/?id=8&nr=2287&page=4&s={paging_id}"

NAME_PREFIX = "Name of the event:"
DATE_PREFIX = "Date:"


class UnknownMatchError(ValueError):
    pass


@dataclass
class Participant:
    name: str
    id: Optional[int] = None


@dataclass
class Match:
    stipulation: str
    winning_side: Optional[List[Participant]]
    losing_side: Optional[List[Participant]]
    draw: bool = False


@dataclass
class Event:
    title: str
    date: datetime.datetime
    matches: List[Match]
