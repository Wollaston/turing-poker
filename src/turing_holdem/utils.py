import random
from enum import Enum
from itertools import combinations, product

from pydantic import BaseModel, ConfigDict, computed_field


class Rank(str, Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "Jack"
    QUEEN = "Queen"
    KING = "King"
    ACE = "Ace"

    @classmethod
    def random(cls) -> "Rank":
        return random.choice(list(cls))


class Suit(str, Enum):
    SPADES = "Spades"
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"

    @classmethod
    def random(cls) -> "Suit":
        return random.choice(list(cls))


class PlayerState(str, Enum):
    ACTIVE = "Active"
    FOLDED = "Folder"


class Action(str, Enum):
    CHECK = "Check"
    CALL = "Call"
    RAISE = "Raise"
    FOLD = "Fold"
    ALL_IN = "All In"


class Card(BaseModel):
    model_config = ConfigDict(frozen=True)

    rank: Rank
    suit: Suit

    @classmethod
    def random(cls) -> "Card":
        return cls(rank=Rank.random(), suit=Suit.random())


class Hand(BaseModel):
    model_config = ConfigDict(frozen=True)

    first: Card
    second: Card

    @classmethod
    def random(cls) -> "Hand":
        return cls(first=Card.random(), second=Card.random())

    @computed_field()
    @property
    def cards(self) -> set[Card]:
        return {self.first, self.second}


class Personality(BaseModel):
    model_config = ConfigDict(frozen=True)

    random_choice_weights: frozenset[int]
    strong: set[Hand]
    middle: set[Hand]
    speculative: set[Hand]

    @computed_field()
    @property
    def hands(self) -> set[Hand]:
        return self.strong | self.middle | self.speculative

    def random_action(self) -> Action:
        options = [action for action in Action if action is not Action.FOLD]
        return random.choices(options, list(self.random_choice_weights), k=1)[0]


PairsSixAndUp: set[Hand] = {
    Hand(
        first=Card(rank=rank, suit=first_suit),
        second=Card(rank=rank, suit=second_suit),
    )
    for rank, (first_suit, second_suit) in product(list(Rank)[4:], product(Suit, Suit))
}

Pairs: set[Hand] = {
    Hand(
        first=Card(rank=rank, suit=first_suit),
        second=Card(rank=rank, suit=second_suit),
    )
    for rank, (first_suit, second_suit) in product(Rank, product(Suit, Suit))
}

NinePercent: Personality = Personality(
    random_choice_weights=frozenset({94, 5, 1, 0}),
    strong=PairsSixAndUp,  # Pairs Six and Up
    middle={
        Hand(
            first=Card(rank=Rank.ACE, suit=suit),
            second=Card(rank=rank, suit=suit),
        )
        for rank, suit in zip([Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE], Suit)
    }
    - Pairs,
    speculative={
        Hand(
            first=Card(rank=Rank.QUEEN, suit=suit),
            second=Card(rank=Rank.KING, suit=suit),
        )
        for suit in Suit
    }
    - Pairs,
)


FifteenPercent: Personality = Personality(
    random_choice_weights=frozenset({90, 8, 2, 0}),
    strong=Pairs,  # all pairs
    middle={
        Hand(
            first=Card(rank=first_rank, suit=suit),
            second=Card(rank=second_rank, suit=suit),
        )
        for (first_rank, second_rank), suit in product(
            zip(list(Rank)[4:-1], list(Rank)[5:]), Suit
        )
    }
    | {
        Hand(first=Card(rank=a, suit=c), second=Card(rank=b, suit=c))
        for (a, b), c in product(
            combinations([Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK], 2),
            Suit,
        )
    }
    | {
        Hand(
            first=Card(rank=Rank.ACE, suit=suit),
            second=Card(rank=Rank.TEN, suit=suit),
        )
        for suit in Suit
    }
    - Pairs,
    speculative={
        Hand(
            first=Card(rank=first_rank, suit=first_suit),
            second=Card(rank=second_rank, suit=second_suit),
        )
        for (first_rank, second_rank), (first_suit, second_suit) in product(
            combinations([Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK], 2),
            product(Suit, Suit),
        )
    }
    - Pairs,
)

TwentyPercent: Personality = Personality(
    random_choice_weights=frozenset({80, 15, 5, 0}),
    strong=Pairs,  # all pairs
    middle={
        Hand(
            first=Card(rank=first_rank, suit=suit),
            second=Card(rank=second_rank, suit=suit),
        )
        for (first_rank, second_rank), suit in product(
            zip(list(Rank)[3:-1], list(Rank)[4:]), Suit
        )
    }
    | {
        Hand(first=Card(rank=a, suit=c), second=Card(rank=b, suit=c))
        for (a, b), c in product(
            combinations([Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK, Rank.TEN], 2),
            Suit,
        )
    }
    | {
        Hand(
            first=Card(rank=Rank.JACK, suit=suit),
            second=Card(rank=Rank.NINE, suit=suit),
        )
        for suit in Suit
    }
    | {
        Hand(
            first=Card(rank=Rank.TEN, suit=suit),
            second=Card(rank=Rank.EIGHT, suit=suit),
        )
        for suit in Suit
    }
    - Pairs,
    speculative={
        Hand(
            first=Card(rank=first_rank, suit=first_suit),
            second=Card(rank=second_rank, suit=second_suit),
        )
        for (first_rank, second_rank), (first_suit, second_suit) in product(
            combinations([Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK, Rank.TEN], 2),
            product(Suit, Suit),
        )
    }
    - Pairs,
)

TwentyFivePercent: Personality = Personality(
    random_choice_weights=frozenset({75, 20, 5, 0}),
    strong=Pairs,  # all pairs
    middle={
        Hand(
            first=Card(rank=first_rank, suit=suit),
            second=Card(rank=second_rank, suit=suit),
        )
        for (first_rank, second_rank), suit in product(
            zip(list(Rank)[3:-1], list(Rank)[4:]), Suit
        )
    }
    | {
        Hand(
            first=Card(rank=first_rank, suit=suit),
            second=Card(rank=second_rank, suit=suit),
        )
        for (first_rank, second_rank), suit in product(
            zip(list(Rank)[4:-1], list(Rank)[6:]), Suit
        )
    }
    | {
        Hand(first=Card(rank=a, suit=c), second=Card(rank=b, suit=c))
        for (a, b), c in product(
            combinations(
                [Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK, Rank.TEN, Rank.NINE], 2
            ),
            Suit,
        )
    }
    | {
        Hand(
            first=Card(rank=Rank.ACE, suit=suit),
            second=Card(rank=Rank.EIGHT, suit=suit),
        )
        for suit in Suit
    }
    | {
        Hand(
            first=Card(rank=Rank.ACE, suit=suit),
            second=Card(rank=Rank.SEVEN, suit=suit),
        )
        for suit in Suit
    }
    - Pairs,
    speculative={
        Hand(
            first=Card(rank=first_rank, suit=first_suit),
            second=Card(rank=second_rank, suit=second_suit),
        )
        for (first_rank, second_rank), (first_suit, second_suit) in product(
            combinations([Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK, Rank.TEN], 2),
            product(Suit, Suit),
        )
    }
    | {
        Hand(
            first=Card(rank=Rank.ACE, suit=first_suit),
            second=Card(rank=Rank.NINE, suit=second_suit),
        )
        for first_suit, second_suit in product(Suit, Suit)
    }
    | {
        Hand(
            first=Card(rank=Rank.TEN, suit=first_suit),
            second=Card(rank=Rank.NINE, suit=second_suit),
        )
        for first_suit, second_suit in product(Suit, Suit)
    }
    - Pairs,
)


ThirtyFivePercent: Personality = Personality(
    random_choice_weights=frozenset({50, 30, 10, 10}),
    strong=Pairs,  # all pairs
    middle={
        Hand(
            first=Card(rank=first_rank, suit=suit),
            second=Card(rank=second_rank, suit=suit),
        )
        for (first_rank, second_rank), suit in product(
            zip(list(Rank)[2:-1], list(Rank)[3:]), Suit
        )
    }
    | {
        Hand(
            first=Card(rank=first_rank, suit=suit),
            second=Card(rank=second_rank, suit=suit),
        )
        for (first_rank, second_rank), suit in product(
            zip(list(Rank)[4:-1], list(Rank)[6:]), Suit
        )
    }
    | {
        Hand(first=Card(rank=a, suit=c), second=Card(rank=b, suit=c))
        for (a, b), c in product(
            combinations(
                [
                    Rank.ACE,
                    Rank.KING,
                    Rank.QUEEN,
                    Rank.JACK,
                    Rank.TEN,
                    Rank.NINE,
                    Rank.EIGHT,
                ],
                2,
            ),
            Suit,
        )
    }
    | {
        Hand(
            first=Card(rank=Rank.ACE, suit=suit),
            second=Card(rank=rank, suit=suit),
        )
        for rank, suit in zip(Rank, Suit)
        if rank is not Rank.ACE
    }
    | {
        Hand(
            first=Card(rank=Rank.TEN, suit=suit),
            second=Card(rank=Rank.SEVEN, suit=suit),
        )
        for suit in Suit
    }
    - Pairs,
    speculative={
        Hand(
            first=Card(rank=first_rank, suit=first_suit),
            second=Card(rank=second_rank, suit=second_suit),
        )
        for (first_rank, second_rank), (first_suit, second_suit) in product(
            combinations(
                [Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK, Rank.TEN, Rank.NINE], 2
            ),
            product(Suit, Suit),
        )
    }
    | {
        Hand(
            first=Card(rank=Rank.ACE, suit=first_suit),
            second=Card(rank=rank, suit=second_suit),
        )
        for rank, (first_suit, second_suit) in product(Rank, product(Suit, Suit))
    }
    - Pairs,
)


FiftyPercent: Personality = Personality(
    random_choice_weights=frozenset({10, 40, 25, 25}),
    strong=Pairs,  # all pairs
    middle={
        Hand(
            first=Card(rank=first_rank, suit=suit),
            second=Card(rank=second_rank, suit=suit),
        )
        for (first_rank, second_rank), suit in product(
            zip(list(Rank)[1:-1], list(Rank)[2:]), Suit
        )
    }
    | {
        Hand(
            first=Card(rank=first_rank, suit=suit),
            second=Card(rank=second_rank, suit=suit),
        )
        for (first_rank, second_rank), suit in product(
            zip(list(Rank)[4:-1], list(Rank)[6:]), Suit
        )
    }
    | {
        Hand(first=Card(rank=a, suit=c), second=Card(rank=b, suit=c))
        for (a, b), c in product(
            combinations(
                [
                    Rank.ACE,
                    Rank.KING,
                    Rank.QUEEN,
                    Rank.JACK,
                    Rank.TEN,
                    Rank.NINE,
                    Rank.EIGHT,
                    Rank.SEVEN,
                ],
                2,
            ),
            Suit,
        )
    }
    | {
        Hand(
            first=Card(rank=Rank.ACE, suit=suit),
            second=Card(rank=rank, suit=suit),
        )
        for rank, suit in zip(Rank, Suit)
    }
    | {
        Hand(
            first=Card(rank=Rank.KING, suit=suit),
            second=Card(rank=rank, suit=suit),
        )
        for rank, suit in zip(Rank, Suit)
    }
    | {
        Hand(
            first=Card(rank=Rank.NINE, suit=suit),
            second=Card(rank=Rank.SIX, suit=suit),
        )
        for suit in Suit
    }
    - Pairs,
    speculative={
        Hand(
            first=Card(rank=first_rank, suit=first_suit),
            second=Card(rank=second_rank, suit=second_suit),
        )
        for (first_rank, second_rank), (first_suit, second_suit) in product(
            combinations(
                [
                    Rank.ACE,
                    Rank.KING,
                    Rank.QUEEN,
                    Rank.JACK,
                    Rank.TEN,
                    Rank.NINE,
                    Rank.EIGHT,
                ],
                2,
            ),
            product(Suit, Suit),
        )
    }
    | {
        Hand(
            first=Card(rank=Rank.ACE, suit=first_suit),
            second=Card(rank=rank, suit=second_suit),
        )
        for rank, (first_suit, second_suit) in product(Rank, product(Suit, Suit))
    }
    | {
        Hand(
            first=Card(rank=Rank.KING, suit=first_suit),
            second=Card(rank=rank, suit=second_suit),
        )
        for rank, (first_suit, second_suit) in product(Rank, product(Suit, Suit))
    }
    | {
        Hand(
            first=Card(rank=first_rank, suit=first_suit),
            second=Card(rank=second_rank, suit=second_suit),
        )
        for (first_rank, second_rank), (first_suit, second_suit) in product(
            zip(list(Rank)[4:-1], list(Rank)[5:]), product(Suit, Suit)
        )
    }
    - Pairs,
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
