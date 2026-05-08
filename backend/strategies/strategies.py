import pandas as pd

def generate_momentum_signal(df, window=20):
    df = df.copy()

    df["momentum"] = df["Close"].pct_change(window)

    df["signal"] = 0
    df.loc[df["momentum"] > 0, "signal"] = 1

    return df


def generate_mean_reversion_signal(df, window=20, threshold=2):
    df = df.copy()

    rolling_mean = df["Close"].rolling(window).mean()
    rolling_std = df["Close"].rolling(window).std()

    z_score = (df["Close"] - rolling_mean) / rolling_std

    df["signal"] = 0
    df.loc[z_score < -threshold, "signal"] = 1
    df.loc[z_score > threshold, "signal"] = -1

    return df