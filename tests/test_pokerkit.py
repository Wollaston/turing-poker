from pokerkit import Automation, Mode, NoLimitTexasHoldem
from pprint import pprint


def test_pokerkit() -> None:
    state = (
        NoLimitTexasHoldem.create_state(
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
            mode=Mode.CASH_GAME,
        ),
    )[0]
    pprint(state)
    # pprint(state.actor_index)
    # pprint(state.check_or_call())
    #
    # pprint(state.actor_index)
    # pprint(state.complete_bet_or_raise_to(100))
    #
    # pprint(state.actor_index)
    # pprint(state.check_or_call())
    #
    # pprint(state.actor_index)
    # pprint(state.complete_bet_or_raise_to(500))
    #
    # pprint(state.actor_index)
    # pprint(state.fold())
    # pprint(state.folded_status)
