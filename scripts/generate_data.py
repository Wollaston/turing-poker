from enum import Enum
from typing import Annotated
from pokerkit import (
    Card,
    calculate_hand_strength,
    Automation,
    NoLimitTexasHoldem,
    Deck,
    StandardHighHand,
)
from concurrent.futures import ProcessPoolExecutor
from pydantic import AfterValidator, BaseModel
from turing_holdem.utils import Action, Personalities
from loguru import logger


class Stats(BaseModel):
    count: int
    averages: dict[str, float]


class StreetType(str, Enum):
    PREFLOP = "Preflop"
    FLOP = "Flop"
    TURN = "Turn"
    RIVER = "River"


class Street(BaseModel):
    street: StreetType
    board: str
    hand_strength: Annotated[float, AfterValidator(lambda x: x if x > 0.0 else 0.0)]
    action: Action


class Simulation(BaseModel):
    personality: str
    hole_cards: str
    preflop: Street
    flop: Street
    turn: Street
    river: Street


class Data(BaseModel):
    name: str
    simulations: list[Simulation] = []


def normalize_frozenset(frozen: str) -> str:
    return frozen.replace("frozenset", "").replace("{", "").replace("}", "")


def generate_data() -> None:
    PLAYER_COUNT = 6
    STARTING_STACK = 2000
    BLINDS = (25, 50)
    MIN_BET = 50

    for personality in Personalities().personalities:
        logger.info("")
        logger.info(f"Generating data for {personality.name}")
        logger.info("")

        data = Data(name=personality.name)

        with ProcessPoolExecutor() as executor:
            for idx in range(1024):
                logger.info(f"Simulation {idx + 1} [{personality.name}]")
                state = NoLimitTexasHoldem.create_state(
                    (  # pyright: ignore
                        Automation.ANTE_POSTING,
                        Automation.BET_COLLECTION,
                        Automation.BLIND_OR_STRADDLE_POSTING,
                        Automation.CARD_BURNING,
                        Automation.HOLE_DEALING,
                        Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                        Automation.HAND_KILLING,
                        Automation.CHIPS_PULLING,
                        Automation.RUNOUT_COUNT_SELECTION,  # Cash-game only
                    ),
                    True,  # Uniform antes?
                    0,  # Antes
                    BLINDS,  # Blinds or straddles
                    MIN_BET,  # Min-bet
                    tuple(
                        [STARTING_STACK for _ in range(PLAYER_COUNT)]
                    ),  # Starting stacks
                    PLAYER_COUNT,  # Number of players
                )

                board = frozenset(
                    Card.parse(
                        "".join([str(card[0])[-3:-1] for card in state.board_cards])
                    )
                )
                hand_strength = (
                    calculate_hand_strength(
                        player_count=PLAYER_COUNT,
                        hole_range=[[card for card in state.hole_cards[0]]],
                        board_cards=board,
                        hole_dealing_count=2,
                        board_dealing_count=5,
                        deck=Deck.STANDARD,  # pyright: ignore
                        hand_types=(StandardHighHand,),
                        sample_count=100,
                        executor=executor,
                    )
                    + personality.bias
                )
                preflop: Street = Street(
                    street=StreetType.PREFLOP,
                    board=normalize_frozenset(str(board)),
                    hand_strength=round(hand_strength, 2),
                    action=personality.act(hand_strength),
                )

                [state.check_or_call() for _ in range(PLAYER_COUNT)]
                state.deal_board()
                board = frozenset(
                    Card.parse(
                        "".join([str(card[0])[-3:-1] for card in state.board_cards])
                    )
                )
                hand_strength = (
                    calculate_hand_strength(
                        player_count=PLAYER_COUNT,
                        hole_range=[[card for card in state.hole_cards[0]]],
                        board_cards=board,
                        hole_dealing_count=PLAYER_COUNT,
                        board_dealing_count=len(state.board_cards),
                        deck=Deck.STANDARD,  # pyright: ignore
                        hand_types=(StandardHighHand,),
                        sample_count=100,
                        executor=executor,
                    )
                    + personality.bias
                )
                flop: Street = Street(
                    street=StreetType.FLOP,
                    board=normalize_frozenset(str(board)),
                    hand_strength=round(hand_strength, 2),
                    action=personality.act(hand_strength),
                )

                [state.check_or_call() for _ in range(PLAYER_COUNT)]
                state.deal_board()
                board = frozenset(
                    Card.parse(
                        "".join([str(card[0])[-3:-1] for card in state.board_cards])
                    )
                )
                hand_strength = (
                    calculate_hand_strength(
                        player_count=PLAYER_COUNT,
                        hole_range=[[card for card in state.hole_cards[0]]],
                        board_cards=board,
                        hole_dealing_count=2,
                        board_dealing_count=5,
                        deck=Deck.STANDARD,  # pyright: ignore
                        hand_types=(StandardHighHand,),
                        sample_count=100,
                        executor=executor,
                    )
                    + personality.bias
                )
                turn: Street = Street(
                    street=StreetType.TURN,
                    board=normalize_frozenset(str(board)),
                    hand_strength=round(hand_strength, 2),
                    action=personality.act(hand_strength),
                )

                [state.check_or_call() for _ in range(PLAYER_COUNT)]
                state.deal_board()
                board = frozenset(
                    Card.parse(
                        "".join([str(card[0])[-3:-1] for card in state.board_cards])
                    )
                )
                hand_strength = (
                    calculate_hand_strength(
                        player_count=PLAYER_COUNT,
                        hole_range=[[card for card in state.hole_cards[0]]],
                        board_cards=board,
                        hole_dealing_count=2,
                        board_dealing_count=5,
                        deck=Deck.STANDARD,  # pyright: ignore
                        hand_types=(StandardHighHand,),
                        sample_count=100,
                        executor=executor,
                    )
                ) + personality.bias
                river: Street = Street(
                    street=StreetType.RIVER,
                    board=normalize_frozenset(str(board)),
                    hand_strength=round(hand_strength, 2),
                    action=personality.act(hand_strength),
                )
                simulation = Simulation(
                    personality=personality.name,
                    hole_cards=str(state.hole_cards[0])
                    .replace("[", "(")
                    .replace("]", ")"),
                    preflop=preflop,
                    flop=flop,
                    turn=turn,
                    river=river,
                )
                data.simulations.append(simulation)
        with open(f"data/{personality.name}.json", "w") as file:
            file.write(data.model_dump_json())

        count = len(data.simulations)
        preflop_sum: float = 0.0
        flop_sum: float = 0.0
        turn_sum: float = 0.0
        river_sum: float = 0.0
        for simulation in data.simulations:
            preflop_sum += simulation.preflop.hand_strength
            flop_sum += simulation.flop.hand_strength
            turn_sum += simulation.turn.hand_strength
            river_sum += simulation.river.hand_strength

        stats = Stats(
            count=count,
            averages={
                "preflop_avg": preflop_sum / count,
                "flop_avg": flop_sum / count,
                "turn_avg": turn_sum / count,
                "river_avg": river_sum / count,
            },
        )

        with open(f"data/{personality.name}_summary.json", "w") as file:
            file.write(stats.model_dump_json())


if __name__ == "__main__":
    generate_data()
