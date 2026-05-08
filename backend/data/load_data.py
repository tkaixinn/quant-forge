import pandas as pd

def load_csv(path):

    data = pd.read_csv(path)

    data["Date"] = pd.to_datetime(data["Date"])

    required_columns = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    for column in required_columns:
        if column not in data.columns:
            raise ValueError(f"Missing required column: {column}")

    return data


filename = input("Enter CSV filename: ")

df = load_csv(filename)

print(df.head())