from pathlib import Path
import dspy
from typing import Literal


class PokerAnalyzer(dspy.Signature):
    """
    Review the folling Poker Hand and determine the best action.
    """

    personality: str = dspy.InputField()
    hole_cards: str = dspy.InputField()
    street: str = dspy.InputField()
    board: str = dspy.InputField()

    action: Literal["fold", "check", "call", "raise", "all_in"] = dspy.OutputField()


class PokerModule(dspy.Module):
    def __init__(self):
        self.preflop_module = dspy.ChainOfThought(PokerAnalyzer)
        self.flop_module = dspy.ChainOfThought(PokerAnalyzer)
        self.turn_module = dspy.ChainOfThought(PokerAnalyzer)
        self.river_module = dspy.ChainOfThought(PokerAnalyzer)

    def forward(
        self,
        personality: str,
        hole_cards: str,
        preflop_board: str,
        preflop_street: str,
        flop_board: str,
        flop_street: str,
        turn_board: str,
        turn_street: str,
        river_board: str,
        river_street: str,
    ):
        preflop_pred = self.preflop_module(
            personality=personality,
            hole_cards=hole_cards,
            board=preflop_board,
            street=preflop_street,
        )
        flop_pred = self.flop_module(
            personality=personality,
            hole_cards=hole_cards,
            board=flop_board,
            street=flop_street,
        )
        turn_pred = self.turn_module(
            personality=personality,
            hole_cards=hole_cards,
            board=turn_board,
            street=turn_street,
        )
        river_pred = self.river_module(
            personality=personality,
            hole_cards=hole_cards,
            board=river_board,
            street=river_street,
        )

        return dspy.Prediction(
            preflop=preflop_pred.action,
            flop=flop_pred.action,
            turn=turn_pred.action,
            river=river_pred.action,
        )


def load_dspy_program(path: Path) -> PokerModule:
    program = PokerModule()
    program.load(path=path)

    return program


def get_dspy_lm(model: str = "meta-llama/Llama-3.1-8B-Instruct") -> dspy.LM:
    lm = dspy.LM(
        f"openai/{model}",
        api_base="http://localhost:8000/v1",
        temperature=0.2,
        api_key="NONE",
        max_tokens=2048,
    )
    dspy.configure(lm=lm)
    return lm
