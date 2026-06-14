import numpy as np
import pandas as pd


def compute_returns(portfolio_df):
    portfolio_df = portfolio_df.copy()
    portfolio_df["returns"] = portfolio_df["portfolio_value"].pct_change()
    return portfolio_df["returns"].dropna()


def compute_trade_returns(df):
    """Compute return for each completed buy→sell round trip."""
    trade_returns = []
    entry_price = None

    for _, row in df.iterrows():
        if row["trade_action"] == 1:
            entry_price = row["Close"]
        elif row["trade_action"] == -1 and entry_price is not None:
            trade_return = (row["Close"] - entry_price) / entry_price
            trade_returns.append(trade_return)
            entry_price = None

    return pd.Series(trade_returns)


def sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252):
    excess = returns - risk_free_rate / periods_per_year
    if excess.std(ddof=0) == 0:
        return 0
    return np.sqrt(periods_per_year) * excess.mean() / excess.std(ddof=0)


def max_drawdown(portfolio_series):
    peak = portfolio_series.cummax()
    drawdown = (portfolio_series - peak) / peak
    return drawdown.min()


def cagr(portfolio_series, periods_per_year=252):
    total_return = portfolio_series.iloc[-1] / portfolio_series.iloc[0]
    years = len(portfolio_series) / periods_per_year
    if years == 0:
        return 0
    return total_return ** (1 / years) - 1


def win_rate(returns):
    if len(returns) == 0:
        return 0
    return (returns > 0).sum() / len(returns)


def profit_factor(returns):
    gains = returns[returns > 0].sum()
    losses = abs(returns[returns < 0].sum())
    if losses == 0:
        return np.inf
    return gains / losses