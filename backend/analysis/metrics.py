import numpy as np
import pandas as pd


def compute_returns(portfolio_df):
    portfolio_df = portfolio_df.copy()
    portfolio_df["returns"] = portfolio_df["portfolio_value"].pct_change()
    return portfolio_df["returns"].dropna()


def sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252):
    excess = returns - risk_free_rate / periods_per_year
    if returns.std() == 0:
        return 0
    return np.sqrt(periods_per_year) * excess.mean() / excess.std()


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