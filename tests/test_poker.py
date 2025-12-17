from pprint import pprint

from turing_holdem.utils import (
    FifteenPercent,
    FiftyPercent,
    NinePercent,
    Personalities,
    ThirtyFivePercent,
    TwentyFivePercent,
    TwentyPercent,
)


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
