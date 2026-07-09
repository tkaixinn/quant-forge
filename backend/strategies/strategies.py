import pandas as pd


def generate_momentum_signal(df, window=20):
    df = df.copy()

    df["momentum"] = df["Close"].pct_change(window)

    df["signal"] = 0
    df.loc[df["momentum"] > 0, "signal"] = 1
    df.loc[df["momentum"] < 0, "signal"] = -1

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


def generate_rsi_signal(df, window=14, overbought=70, oversold=30):
    """
    RSI (Relative Strength Index) strategy.
    Buy when RSI < oversold, sell when RSI > overbought.
    """
    df = df.copy()


    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    df["signal"] = 0
    df.loc[df["rsi"] < oversold, "signal"] = 1  
    df.loc[df["rsi"] > overbought, "signal"] = -1  

    return df


def generate_macd_signal(df, fast=12, slow=26, signal_window=9):
    """
    MACD (Moving Average Convergence Divergence) strategy.
    Buy when MACD crosses above signal line, sell when it crosses below.
    """
    df = df.copy()


    ema_fast = df["Close"].ewm(span=fast).mean()
    ema_slow = df["Close"].ewm(span=slow).mean()
    df["macd"] = ema_fast - ema_slow
    df["macd_signal"] = df["macd"].ewm(span=signal_window).mean()
    df["macd_diff"] = df["macd"] - df["macd_signal"]

  
    df["signal"] = 0
    df.loc[df["macd_diff"] > 0, "signal"] = 1  
    df.loc[df["macd_diff"] < 0, "signal"] = -1  

    return df


def generate_bollinger_bands_signal(df, window=20, num_std=2):
    """
    Bollinger Bands strategy.
    Buy when price touches lower band, sell when price touches upper band.
    """
    df = df.copy()

  
    rolling_mean = df["Close"].rolling(window).mean()
    rolling_std = df["Close"].rolling(window).std()
    df["bb_upper"] = rolling_mean + (rolling_std * num_std)
    df["bb_lower"] = rolling_mean - (rolling_std * num_std)
    df["bb_middle"] = rolling_mean


    df["signal"] = 0
    df.loc[df["Close"] < df["bb_lower"], "signal"] = 1  
    df.loc[df["Close"] > df["bb_upper"], "signal"] = -1  

    return df