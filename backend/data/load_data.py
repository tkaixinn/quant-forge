import pandas as pd
import pathlib

def load_csv(filename):

    base_dir = pathlib.Path(__file__).resolve().parent
    path = base_dir / filename

    if not path.exists():
        raise FileNotFoundError(f"CSV not found in data folder: {path}")

    df = pd.read_csv(path)

    if "Date" not in df.columns:
        df = df.rename(columns={df.columns[0]: "Date"})

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    required = ["Date", "Open", "High", "Low", "Close", "Volume"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    return df, path