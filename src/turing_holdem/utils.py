import random
from enum import Enum

from loguru import logger
import pokerkit
from pydantic import BaseModel, ConfigDict, computed_field
from pokerkit import parse_range


class Action(str, Enum):
    CHECK = "check"
    CALL = "call"
    RAISE = "raise"
    FOLD = "fold"
    ALL_IN = "all_in"

    @classmethod
    def from_str(cls, action: str) -> "Action":
        if action == "check":
            return Action.CHECK
        elif action == "call":
            return Action.CALL
        elif action == "raise":
            return Action.RAISE
        elif action == "fold":
            return Action.FOLD
        elif action == "all_in":
            return Action.ALL_IN
        else:
            logger.error(f"Invalid action provided: {action}. Defaulting to FOLD.")
            return Action.FOLD


class Personality(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    bias: float
    strong: set[frozenset[pokerkit.Card]]
    middle: set[frozenset[pokerkit.Card]]
    speculative: set[frozenset[pokerkit.Card]]

    @computed_field()
    @property
    def range(self) -> set[frozenset[pokerkit.Card]]:
        return self.strong | self.middle | self.speculative

    def act(self, hand_strength: float) -> Action:
        if hand_strength > 0.7:
            return Action.ALL_IN
        elif hand_strength > 0.5:
            return Action.RAISE
        elif hand_strength > 0.3:
            return Action.CALL
        elif hand_strength > 0.2:
            return Action.CHECK
        else:
            return Action.FOLD


NinePercent: Personality = Personality(
    name="nine_percent",
    bias=0.0,
    strong=parse_range("66+"),  # Pairs Six and Up
    middle=parse_range("AJs+;KQs"),
    speculative=parse_range("AJo+;KQo"),
)


FifteenPercent: Personality = Personality(
    name="fifteen_percent",
    bias=0.05,
    strong=parse_range("22+"),
    middle=parse_range("ATs+;KJs+;QJs;JTs;T9s;98s;87s;76s;65s"),
    speculative=parse_range("AJo+;KJo+;QJo"),
)

TwentyPercent: Personality = Personality(
    name="twenty_percent",
    bias=0.1,
    strong=parse_range("22+"),
    middle=parse_range("ATs+;KTs+;QTs+;J9s+;T8s+;98s;87s;76s;65s;54s"),
    speculative=parse_range("ATo+;KTo+;QTo+;JTo"),
)


TwentyFivePercent: Personality = Personality(
    name="twenty_five_percent",
    bias=0.15,
    strong=parse_range("22+"),
    middle=parse_range("A7s+;K9s+;Q9s+;J9s+;T8s+;97s+;86s+;75s+;64s+;54s"),
    speculative=parse_range("A9o+;KTo+;QTo+;JTo;T9o"),
)


ThirtyFivePercent: Personality = Personality(
    name="thirty_five_percent",
    bias=0.2,
    strong=parse_range("22+"),
    middle=parse_range("A2s+;K8s+;Q8s+;J8s+;T7s+;97s+;86s+;75s+;64s+;54s;43s"),
    speculative=parse_range("A8o+;A2o;A3o;A4o;A5o;K9o+;Q9o+;J9o+;T9o"),
)


FiftyPercent: Personality = Personality(
    name="fifty_percent",
    bias=0.3,
    strong=parse_range("22+"),
    middle=parse_range("A2s+;K2s+;Q7s+;J7s+;T7s+;96s+;86s+;75s+;64s+;53s+;43s"),
    speculative=parse_range("A2o+;K5o+;Q8o+;J8o+;T8o+;98o;87o;76o;65o"),
)


class Personalities(BaseModel):
    model_config = ConfigDict(frozen=True)

    personalities: list[Personality] = [
        NinePercent,
        FifteenPercent,
        TwentyPercent,
        TwentyFivePercent,
        ThirtyFivePercent,
        FiftyPercent,
    ]


def random_name():
    first_names = [
        "Liam",
        "Olivia",
        "Noah",
        "Emma",
        "Oliver",
        "Ava",
        "Elijah",
        "Sophia",
        "James",
        "Isabella",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Miller",
        "Davis",
        "Garcia",
        "Rodriguez",
        "Wilson",
    ]

    first_name = random.choice(first_names)
    last_name = random.choice(last_names)

    return f"{first_name} {last_name}"
