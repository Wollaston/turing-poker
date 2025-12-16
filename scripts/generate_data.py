from pydantic import BaseModel
from turing_holdem.poker import Deck
from turing_holdem.utils import Action, Card, Hand, Personalities
import random


class Rotation(BaseModel):
    hand: Hand
    flop: set[Card]
    turn: set[Card]
    river: set[Card]
    actions: list[Action] = []

    @classmethod
    def random(cls, deck: Deck) -> "Rotation":
        return cls(
            hand=deck.random_hand(),
            flop=deck.flop(),
            turn=deck.turn(),
            river=deck.river(),
        )


class Data(BaseModel):
    name: str
    rotations: list[Rotation] = []


names = [
    "NinePercent",
    "FifteenPercent",
    "TwentyPercent",
    "TwentyFivePercent",
    "ThirtyFivePercent",
    "FiftyPercent",
]


def generate_data() -> None:
    for name, personality in zip(names, Personalities().personalities):
        data = Data(name=name)
        for _ in range(100):
            deck = Deck()
            hand = {deck.random_hand()}

            random_action = personality.random_action()
            if hand in personality.strong:
                base = Action.RAISE
            elif hand in personality.middle:
                base = Action.CALL
            else:
                base = Action.CHECK
            preflop_action: Action = random.choice([random_action, base])

            flop = deck.flop()
            random_action = personality.random_action()
            if hand <= flop:
                base = Action.RAISE
            elif bool(hand & flop):
                base = Action.CALL
            else:
                base = Action.CHECK
            flop_action: Action = random.choice([random_action, base])

            turn = deck.turn()
            random_action = personality.random_action()
            if bool(hand & turn):
                base = Action.RAISE
            else:
                base = Action.CHECK
            turn_action: Action = random.choice([random_action, base])

            river = deck.river()
            random_action = personality.random_action()
            if bool(hand & river):
                base = Action.RAISE
            else:
                base = Action.CHECK
            river_action: Action = random.choice([random_action, base])

            data.rotations.append(
                Rotation(
                    hand=hand.pop(),
                    flop=flop,
                    turn=turn,
                    river=river,
                    actions=[preflop_action, flop_action, turn_action, river_action],
                )
            )
        with open(f"data/{data.name}.json", "w") as file:
            file.write(data.model_dump_json())


if __name__ == "__main__":
    generate_data()
