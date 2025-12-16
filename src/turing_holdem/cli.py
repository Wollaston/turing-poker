import typer

app = typer.Typer(pretty_exceptions_enable=False)


@app.command()
def play():
    print("Hello from turing-holdem!")


def cli() -> None:
    app()
