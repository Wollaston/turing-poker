import pokerkit
from pydantic import BaseModel, Field

from pokerkit import Automation, NoLimitTexasHoldem, State
from loguru import logger

from .utils import (
    Personalities,
    Personality,
    random_name,
)


class Player(BaseModel):
    name: str = Field(default_factory=lambda: random_name())
    personality: Personality
    idx: int


class Poker(BaseModel):
    players: dict[int, Player]
    state: State
    over: bool = False
    current_round: int = 1

    @classmethod
    def new_game(cls) -> "Poker":
        return Poker(
            players={
                idx: Player(personality=personality, idx=idx)
                for idx, personality in enumerate(Personalities().personalities)
            },
            state=NoLimitTexasHoldem.create_state(
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
                raw_starting_stacks={
                    0: 1000,
                    1: 1000,
                    2: 1000,
                    3: 1000,
                    4: 1000,
                    5: 1000,
                },  # starting stacks
                player_count=6,  # number of players
            ),
        )

    def play(self) -> None:
        self._game_info()

        self.round()

    def round(self) -> None:
        self._show_round()

    def _current_player(self) -> Player:
        try:
            return self.players[self.state.actor_index]  # pyright: ignore
        except Exception as e:
            raise ValueError(e)

    def _current_hand(self) -> tuple[pokerkit.Card, ...]:
        try:
            return tuple(self.state.get_down_cards(self.state.actor_index))  # pyright: ignore
        except Exception as e:
            raise ValueError(e)

    def _get_players(self) -> None:
        logger.info("")
        logger.info("There are the following players in the game:")
        for _ in list(self.state.actor_indices):
            logger.info(
                f"\t{self._current_player().name} [Index {self.state.actor_index}]"
            )
            self.state.check_or_call()

    def _show_round(self) -> None:
        logger.info("")
        logger.info(f"The current round is {self.current_round}")
        logger.info(f"There are {len(self.state.actor_indices)} players")
        logger.info("")

    def _game_info(self) -> None:
        logger.info("")
        logger.info("Starting a game of poker:")
        self._get_players()
        logger.info("The game has the following configuration:")
        logger.info(f"\tPlayers: {self.state.player_count}")
        logger.info(f"\tSmall Blind: {self.state.blinds_or_straddles[0]}")
        logger.info(f"\tBig Blind: {self.state.blinds_or_straddles[1]}")
        logger.info(f"\tMinimum Bet: {self.state.blinds_or_straddles[1]}")
        logger.info("\tStarting Stacks:")
        for idx, value in enumerate(self.state.starting_stacks):
            logger.info(f"\t\tStarting stack for {self.players[idx].name}: {value}")
