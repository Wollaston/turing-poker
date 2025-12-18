import glob
import pandas as pd


def count() -> None:
    total = pd.DataFrame()
    paths = glob.glob("reports/*")
    for path in paths:
        with open(path, "r") as file:
            counts = pd.read_json(file)
            total = pd.concat([total, counts])

    print(len(total))
    print(total.value_counts())
    print(total.value_counts(normalize=True))


if __name__ == "__main__":
    count()
