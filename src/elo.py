from typing import Set, Union, List

from src.constants import Wrestler


class Elo:
    def __init__(self, wrestlers: Set[Wrestler]) -> None:
        self.wrestlers_to_rating = {k: 1500 for k in wrestlers}

    def update_rating(
        self, winners: List[Wrestler], losers: List[Wrestler], draw: bool
    ) -> None:
        k = 12 if len(losers) > len(winners) else 32
        winners_elo = sum(self.wrestlers_to_rating[winner] for winner in winners) / len(
            winners
        )
        losers_elo = sum(self.wrestlers_to_rating[loser] for loser in losers) / len(
            losers
        )

        expected_result = self.expected_result(winners_elo, losers_elo)

        if draw:
            for wrestler in winners + losers:
                self.wrestlers_to_rating[wrestler] += k * expected_result
            return

        for winner in winners:
            self.wrestlers_to_rating[winner] += k * (1 - expected_result)

        for loser in losers:
            self.wrestlers_to_rating[loser] += k * (expected_result - 1)

    @staticmethod
    def expected_result(first: Union[int, float], second: Union[int, float]) -> float:
        exp = (second - first) / 400.0
        return 1 / ((10.0 ** exp) + 1)
