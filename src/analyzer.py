import datetime
from pathlib import Path
from pprint import pprint
from typing import List, Set

import pandas as pd

from constants import Event, Wrestler
from elo import Elo
from utils import find_same_ids, create_list_of_events, get_all_wrestlers


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


def analyze(path: Path, to_save: bool = False) -> pd.DataFrame:
    events = _clean_up_wrestler_references(
        _sort_by_date(_merge_same_ids(create_list_of_events(path)))
    )
    all_wrestlers = get_all_wrestlers(events)
    elo = Elo(all_wrestlers)

    sorted_dates = sorted({event.date.date() for event in events})

    df = pd.DataFrame(index=elo.wrestlers_to_rating, columns=sorted_dates)

    for event in events:
        date = event.date.date()
        for match in event.matches:
            elo.update_rating(match.winning_side, match.losing_side, match.draw)
        df[date] = pd.Series(elo.wrestlers_to_rating)

    if to_save:
        df.to_csv(str(path / "results.csv"))
    return df
