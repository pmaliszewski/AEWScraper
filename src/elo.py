from typing import Set, Union

from src.constants import Wrestler


class Elo:
    def __init__(self, wrestlers: Set[Wrestler], k: int) -> None:
        self.wrestlers = {k: 1500 for k in wrestlers}
        self.k = k

    def add_wrestler(self, wrestler: Wrestler, rating: int = 1500) -> None:
        self.wrestlers[wrestler] = rating

    def expected_result(
        self, first: Union[int, float], second: Union[int, float]
    ) -> float:
        exp = (second - first) / 400.0
        return 1 / ((10.0 ** (exp)) + 1)
