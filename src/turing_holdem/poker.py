from pathlib import Path
import dspy
from pydantic import BaseModel, ConfigDict, Field

from pokerkit import Automation, NoLimitTexasHoldem, State
from loguru import logger

from turing_holdem.dspy_modules import PokerModule, load_dspy_program, get_dspy_lm
from .utils import (
    Action,
    Personalities,
    Personality,
    random_name,
)
import uuid


class Player(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(default_factory=lambda: random_name())
    personality: Personality
    program: PokerModule
    idx: int


class Poker(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    players: dict[int, Player]
    game: NoLimitTexasHoldem
    over: bool = False
    current_round: int = 1
    lm: dspy.LM = Field(default_factory=lambda: get_dspy_lm())
    board_index: int = 0
    starting_stacks: dict[int, int] = {
        0: 1000,
        1: 1000,
        2: 1000,
        3: 1000,
        4: 1000,
        5: 1000,
    }
    player_count: int = 6
    winners: list[str] = []

    @classmethod
    def new_game(cls, programs: list[Path]) -> "Poker":
        return Poker(
            players={
                idx: Player(
                    personality=personality,
                    idx=idx,
                    program=load_dspy_program(program),
                )
                for idx, (personality, program) in enumerate(
                    zip(Personalities().personalities, programs)
                )
            },
            game=NoLimitTexasHoldem(
                automations=(  # pyright: ignore
                    Automation.ANTE_POSTING,
                    Automation.BET_COLLECTION,
                    Automation.BLIND_OR_STRADDLE_POSTING,
                    Automation.CARD_BURNING,
                    Automation.HOLE_DEALING,
                    Automation.BOARD_DEALING,
                    Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                    Automation.HAND_KILLING,
                    Automation.CHIPS_PUSHING,
                    Automation.CHIPS_PULLING,
                    Automation.RUNOUT_COUNT_SELECTION,  # Cash-game only
                ),
                ante_trimming_status=True,  # Uniform antes?
                raw_antes=0,  # Antes
                raw_blinds_or_straddles=(25, 50),  # Blinds or straddles
                min_bet=50,  # Min-bet
            ),
        )

    def new_state(self) -> State:
        return self.game(self.starting_stacks, self.player_count)

    def play(self, hands: int = 100) -> None:
        for idx in range(hands):
            logger.info(f"Hand {idx + 1}")
            self.hand()
        self.report()

    def hand(self) -> None:
        state = self.new_state()

        for street in ["Preflop", "Flop", "Turn", "River"]:
            logger.info(f"Street: {street}")
            for _ in range(state.player_count):
                if state.actor_index:
                    name = self._current_player(state).name
                    match self._get_action(state, state.actor_index):
                        case Action.ALL_IN:
                            logger.info(f"Player {name} went all in.")
                            state.complete_bet_or_raise_to(
                                state.get_effective_stack(state.actor_index)
                            )
                        case Action.RAISE:
                            if state.can_complete_bet_or_raise_to(
                                state.min_completion_betting_or_raising_to_amount
                            ):
                                logger.info(f"Player {name} raised.")
                                state.complete_bet_or_raise_to(
                                    state.min_completion_betting_or_raising_to_amount
                                )
                            else:
                                logger.info(
                                    f"Player {name} could not raise, so they folded"
                                )
                                state.fold()
                        case Action.CALL:
                            if state.can_check_or_call():
                                logger.info(f"Player {name} called.")
                                state.check_or_call()
                            else:
                                logger.info(
                                    f"Player {name} could not call, so they folded"
                                )
                                state.fold()
                        case Action.CHECK:
                            if state.can_check_or_call():
                                logger.info(f"Player {name} checked.")
                                state.check_or_call()
                            else:
                                logger.info(
                                    f"Player {name} could not check, so they folded"
                                )
                                state.fold()
                        case Action.FOLD:
                            try:
                                logger.info(f"Player {name} folded.")
                                state.fold()
                            except Exception as e:
                                logger.warning(
                                    f"Player {name} wanted to fold, but checks prevented it: {e}."
                                )
                                state.check_or_call()

            [
                state.check_or_call()
                for _ in state.player_indices
                if state.can_check_or_call()
            ]
        winner = state.stacks.index(max(state.stacks))
        self.winners.append(self.players[winner].personality.name)

    def report(self) -> None:
        reports_dir = Path("reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        id = str(uuid.uuid4())[:10]
        with open(f"{reports_dir}/data_{id}.json", "w") as file:
            file.write(self.model_dump_json(include={"winners"}))

    def _get_action(self, state: State, idx: int) -> Action:
        personality = self.players[idx].personality.name
        hole_cards = hole_cards = tuple(state.get_down_cards(idx))
        board = tuple(state.get_board_cards(self.board_index))
        street = self._get_street(state)

        match street:
            case "Preflop":
                return Action.from_str(
                    self.players[idx]
                    .program.preflop_module(
                        personality=personality,
                        hole_cards=hole_cards,
                        board=board,
                        street=street,
                    )
                    .action
                )
            case "Flop":
                return Action.from_str(
                    self.players[idx]
                    .program.flop_module(
                        personality=personality,
                        hole_cards=hole_cards,
                        board=board,
                        street=street,
                    )
                    .action
                )
            case "Turn":
                return Action.from_str(
                    self.players[idx]
                    .program.turn_module(
                        personality=personality,
                        hole_cards=hole_cards,
                        board=board,
                        street=street,
                    )
                    .action
                )
            case "River":
                return Action.from_str(
                    self.players[idx]
                    .program.river_module(
                        personality=personality,
                        hole_cards=hole_cards,
                        board=board,
                        street=street,
                    )
                    .action
                )
            case _:
                raise ValueError(f"Invalid Steet: {state.street_index}")

    def _current_player(self, state: State) -> Player:
        try:
            return self.players[state.actor_index]  # pyright: ignore
        except Exception as e:
            raise ValueError(e)

    def _get_street(self, state: State) -> str:
        match state.street_index:
            case 0:
                return "Preflop"
            case 1:
                return "Flop"
            case 2:
                return "Turn"
            case 3:
                return "River"
            case _:
                raise ValueError(f"Invalid Steet: {state.street_index}")
