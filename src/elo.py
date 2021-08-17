from typing import Set, Union, List

from src.constants import Wrestler


class Elo:
    def __init__(self, wrestlers: Set[Wrestler], k: int) -> None:
        self.wrestlers_to_rating = {k: 1500 for k in wrestlers}
        self.k = k

    def add_wrestler(self, wrestler: Wrestler, rating: int = 1500) -> None:
        self.wrestlers_to_rating[wrestler] = rating

    def update_one_on_one(self, winner: Wrestler, loser: Wrestler) -> None:
        winner_old_elo, loser_old_elo = (
            self.wrestlers_to_rating[winner],
            self.wrestlers_to_rating[loser],
        )
        expected_result = self.expected_result(winner_old_elo, loser_old_elo)
        self.wrestlers_to_rating[winner] = winner_old_elo + self.k * (
            1 - expected_result
        )
        self.wrestlers_to_rating[loser] = loser_old_elo + self.k * (
            -(1 - expected_result)
        )

    def expected_result(
        self, first: Union[int, float], second: Union[int, float]
    ) -> float:
        exp = (second - first) / 400.0
        return 1 / ((10.0 ** exp) + 1)
