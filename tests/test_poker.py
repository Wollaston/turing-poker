from pathlib import Path
from pprint import pprint

from turing_holdem.poker import Poker
from turing_holdem.utils import (
    FifteenPercent,
    FiftyPercent,
    NinePercent,
    ThirtyFivePercent,
    TwentyFivePercent,
    TwentyPercent,
)

PROGRAMS = [
    "programs/gepa_fifteen_percent.json",
    "programs/gepa_fifty_percent.json",
    "programs/gepa_nine_percent.json",
    "programs/gepa_thirty_five_percent.json",
    "programs/gepa_twenty_five_percent.json",
    "programs/gepa_twenty_percent.json",
]


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


def test_poker() -> None:
    pprint(Poker.new_game([Path(program) for program in PROGRAMS]).play(3))
