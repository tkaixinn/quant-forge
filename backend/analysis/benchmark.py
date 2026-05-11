import numpy as np


def buy_and_hold_returns(price_series):
    """
    SPY benchmark returns
    """
    return price_series.pct_change().dropna()


def benchmark_metrics(price_series):
    returns = buy_and_hold_returns(price_series)

    cumulative = price_series / price_series.iloc[0]

    return {
        "benchmark_returns": returns,
        "benchmark_cumulative": cumulative
    }