import argparse
import random
from pathlib import Path
from typing import Literal

import dspy
from datasets import DatasetDict, load_dataset

dspy.configure_cache(
    enable_disk_cache=False,
)


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


def get_datasets(
    data: str,
) -> tuple[list[dspy.Example], list[dspy.Example], list[dspy.Example]]:
    dataset = load_dataset("json", data_files=data, field="simulations")

    if not isinstance(dataset, DatasetDict):
        raise TypeError(f"Expected 'DatasetDict', got {type(dataset)}")

    train_test_valid = dataset["train"].train_test_split(test_size=0.4, shuffle=True)
    test_valid = train_test_valid["test"].train_test_split(test_size=0.5, shuffle=True)

    dataset = DatasetDict(
        {
            "train": train_test_valid["train"].flatten(),
            "dev": test_valid["train"].flatten(),
            "test": test_valid["test"].flatten(),
        }
    )

    dspy_train_dataset = [
        dspy.Example(
            {
                "personality": d["personality"],
                "hole_cards": d["hole_cards"],
                "preflop_board": d["preflop.board"],
                "preflop_street": d["preflop.street"],
                "flop_board": d["flop.board"],
                "flop_street": d["flop.street"],
                "turn_board": d["turn.board"],
                "turn_street": d["turn.street"],
                "river_board": d["river.board"],
                "river_street": d["river.street"],
                "preflop_action": d["preflop.action"],
                "flop_action": d["flop.action"],
                "turn_action": d["turn.action"],
                "river_action": d["river.action"],
            }
        ).with_inputs(
            "personality",
            "hole_cards",
            "preflop_board",
            "preflop_street",
            "flop_board",
            "flop_street",
            "turn_board",
            "turn_street",
            "river_board",
            "river_street",
        )
        for d in dataset["train"]
        if isinstance(d, dict)
    ]

    dspy_dev_dataset = [
        dspy.Example(
            {
                "personality": d["personality"],
                "hole_cards": d["hole_cards"],
                "preflop_board": d["preflop.board"],
                "preflop_street": d["preflop.street"],
                "flop_board": d["flop.board"],
                "flop_street": d["flop.street"],
                "turn_board": d["turn.board"],
                "turn_street": d["turn.street"],
                "river_board": d["river.board"],
                "river_street": d["river.street"],
                "preflop_action": d["preflop.action"],
                "flop_action": d["flop.action"],
                "turn_action": d["turn.action"],
                "river_action": d["river.action"],
            }
        ).with_inputs(
            "personality",
            "hole_cards",
            "preflop_board",
            "preflop_street",
            "flop_board",
            "flop_street",
            "turn_board",
            "turn_street",
            "river_board",
            "river_street",
        )
        for d in dataset["dev"]
        if isinstance(d, dict)
    ]

    dspy_test_dataset = [
        dspy.Example(
            {
                "personality": d["personality"],
                "hole_cards": d["hole_cards"],
                "preflop_board": d["preflop.board"],
                "preflop_street": d["preflop.street"],
                "flop_board": d["flop.board"],
                "flop_street": d["flop.street"],
                "turn_board": d["turn.board"],
                "turn_street": d["turn.street"],
                "river_board": d["river.board"],
                "river_street": d["river.street"],
                "preflop_action": d["preflop.action"],
                "flop_action": d["flop.action"],
                "turn_action": d["turn.action"],
                "river_action": d["river.action"],
            }
        ).with_inputs(
            "personality",
            "hole_cards",
            "preflop_board",
            "preflop_street",
            "flop_board",
            "flop_street",
            "turn_board",
            "turn_street",
            "river_board",
            "river_street",
        )
        for d in dataset["test"]
        if isinstance(d, dict)
    ]

    return dspy_train_dataset, dspy_dev_dataset, dspy_test_dataset


def score(gold: str, pred: str) -> tuple[str, float]:
    """
    Compute score for the urgency module.
    """
    score = 1.0 if gold.lower() == pred.lower() else 0.0
    if gold == pred:
        feedback = f"You made the correct '{pred}' action for this hand and board. This correct action is indeed '{gold}.'"
    else:
        feedback = f"You made the incorrect '{pred}' action for this hand and board. The correct action is '{gold}'. Think about how you could have reasoned to make the correct decision with you hand and the board cards."
    return feedback, score


def metric(example, pred, trace=None, pred_name=None, pred_trace=None):
    """
    Computes a score based on agreement between prediction and
    gold standard for preflop, flop, turn and river.
    Returns the score (float).
    """
    preflop_gold = example["preflop_action"]
    flop_gold = example["flop_action"]
    turn_gold = example["turn_action"]
    river_gold = example["river_action"]

    # Compute scores for all modules
    preflop_feedback, score_preflop = score(preflop_gold, pred.preflop)
    flop_feedback, score_flop = score(flop_gold, pred.flop)
    turn_feedback, score_turn = score(turn_gold, pred.turn)
    river_feedback, score_river = score(river_gold, pred.river)

    total = (score_preflop + score_flop + score_turn + score_river) / 4

    if pred_name is None:
        return total
    elif pred_name == "preflop_module.predict":
        feedback = preflop_feedback
    elif pred_name == "flop_module.predict":
        feedback = flop_feedback
    elif pred_name == "turn_module.predict":
        feedback = turn_feedback
    elif pred_name == "river_module.predict":
        feedback = river_feedback
    else:
        raise ValueError("Expected value for feedback")

    return dspy.Prediction(score=total, feedback=feedback)


def optimize(data: Path) -> None:
    random.seed(42)

    lm = dspy.LM(
        "openai/meta-llama/Llama-3.1-8B-Instruct",
        api_base="http://localhost:8000/v1",
        temperature=0.2,
        api_key="NONE",
        max_tokens=2048,
    )
    dspy.configure(lm=lm)

    train_set, dev_set, test_set = get_datasets(str(data))

    program = PokerModule()

    optimizer = dspy.GEPA(
        metric=metric,
        auto="heavy",
        num_threads=16,
        track_stats=True,
        use_merge=False,
        reflection_lm=lm,
    )

    optimized_program = optimizer.compile(
        program,
        trainset=train_set,
        valset=dev_set,
    )

    evaluate = dspy.Evaluate(
        devset=test_set,
        metric=metric,
        num_threads=16,
        display_table=True,
        display_progress=True,
    )

    evaluate(optimized_program)
    print(optimized_program.detailed_results)

    personality = str(data).replace("data/", "").replace(".json", "")
    path = Path("./programs/")
    path.mkdir(parents=True, exist_ok=True)
    program = optimized_program
    optimized_program.save(f"{path}/gepa_{personality}.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train an LLM Poker Agent with GEPA")

    parser.add_argument(
        "data", type=Path, help="The path to the generated personality data"
    )

    args = parser.parse_args()

    optimize(data=args.data)
