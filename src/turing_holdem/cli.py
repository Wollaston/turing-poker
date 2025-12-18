from pathlib import Path
from typing import Annotated
import typer

from turing_holdem.poker import Poker

app = typer.Typer(pretty_exceptions_enable=False)

PROGRAMS = [
    "programs/gepa_fifteen_percent.json",
    "programs/gepa_fifty_percent.json",
    "programs/gepa_nine_percent.json",
    "programs/gepa_thirty_five_percent.json",
    "programs/gepa_twenty_five_percent.json",
    "programs/gepa_twenty_percent.json",
]


@app.command()
def play(
    hands: Annotated[
        int, typer.Option(prompt="The number of hands to play in this simulation")
    ] = 100,
):
    Poker.new_game([Path(program) for program in PROGRAMS]).play(hands)


def cli() -> None:
    app()
