from itertools import product
from pprint import pprint

from turing_holdem.poker import Poker
from turing_holdem.utils import (
    Card,
    Hand,
    Personalities,
    Rank,
    Suit,
    FifteenPercent,
    FiftyPercent,
    NinePercent,
    PairsSixAndUp,
    ThirtyFivePercent,
    TwentyFivePercent,
    TwentyPercent,
)


def test_pairs_six_and_up() -> None:
    pprint(PairsSixAndUp)


def test_ninep() -> None:
    pprint(NinePercent)


def test_fifteenp() -> None:
    pprint(FifteenPercent.middle)


def test_twentyp() -> None:
    pprint(TwentyPercent)


def test_twentyfivep() -> None:
    pprint(TwentyFivePercent)


def test_thirtyfivep() -> None:
    pprint(ThirtyFivePercent)


def test_fiftyp() -> None:
    pprint(FiftyPercent)


def test_personalities() -> None:
    for personality in Personalities().personalities:
        print(len(personality.hands))


def test_product() -> None:
    pprint(
        {
            Hand(
                first=Card(rank=rank, suit=first_suit),
                second=Card(rank=rank, suit=second_suit),
            )
            for rank, (first_suit, second_suit) in product(Rank, product(Suit, Suit))
        }
    )


def test_poker() -> None:
    pprint(Poker.new_game())


def test_poker_play() -> None:
    pprint(Poker.new_game().play())
