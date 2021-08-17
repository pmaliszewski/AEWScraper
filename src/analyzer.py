from typing import List, Set

from constants import Event, Participant
from utils import find_same_ids


def _clean_up_participant_references(events: List[Event]) -> List[Event]:
    cache: Set[Participant] = set()
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
                    if wrestler.participant_id == k and wrestler.name != common_name:
                        wrestler.name = common_name
    return events


# def basic_analyze(path: Path = Path("C:/Users/Paweł/Desktop/dumps")):
#     events = _sort_by_date(_merge_same_ids(create_list_of_events(Path(path))))
#     events = _clean_up_participant_references(events)
#     participant_to_player = {}
#     for event in events:
#         for match in event.matches:
#             for participant in match.winning_side + match.losing_side:
#                 if participant.name not in participant_to_player:
#                     participant_to_player[participant.name] = Player()
#     for event in events:
#         for match in event.matches:
#             if len(match.winning_side) == 1 and len(match.losing_side) == 1:
#                 orig_winner = participant_to_player[
#                     match.winning_side[0].name
#                 ].getRating()
#                 participant_to_player[match.winning_side[0].name].update_player(
#                     [participant_to_player[match.losing_side[0].name].getRating()],
#                     [100],
#                     [1],
#                 )
#                 participant_to_player[match.losing_side[0].name].update_player(
#                     [orig_winner], [100], [0]
#                 )
#     final_elos = {}
#     for k, v in participant_to_player.items():
#         final_elos[k] = v.getRating()
#     sorted_elos = {
#         k: v for k, v in sorted(final_elos.items(), key=lambda item: item[1])
#     }
#     pprint(sorted_elos)
#
#
# basic_analyze()
# pprint(find_same_ids(_merge_same_ids(create_list_of_events(Path("C:/Users/Paweł/Desktop/dumps")))))
