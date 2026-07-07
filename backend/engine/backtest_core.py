import pandas as pd
import yfinance as yf
from datetime import timedelta
from analysis.report import generate_strategy_report
from strategies.strategies import (
    generate_momentum_signal,
    generate_mean_reversion_signal,
    generate_rsi_signal,
    generate_macd_signal,
    generate_bollinger_bands_signal,
)
from engine.portfolio import Portfolio
from engine.execution import execute_buy, execute_sell


def run_backtest(
    df,
    strategy_name,
    initial_cash=10000,
    strategy_params=None,
    benchmark_ticker="SPY"
):

    if strategy_params is None:
        strategy_params = {}

    df = df.copy()

    benchmark_start = pd.to_datetime(df["Date"].iloc[0])
    benchmark_end = pd.to_datetime(df["Date"].iloc[-1]) + timedelta(days=1)

    spy_df = yf.download(
        benchmark_ticker,
        start=benchmark_start,
        end=benchmark_end,
        progress=False
    )
    spy_df = spy_df.reset_index()

    if isinstance(spy_df.columns, pd.MultiIndex):
        new_cols = []
        for col in spy_df.columns.values:
            if isinstance(col, tuple):
                parts = [str(c) for c in col if c and str(c).strip()]
                new_cols.append("_".join(parts))
            else:
                new_cols.append(str(col))
        spy_df.columns = new_cols

    if "Close_SPY" in spy_df.columns:
        spy_df = spy_df.rename(columns={"Close_SPY": "SPY_Close"})
    elif "SPY_Close" not in spy_df.columns and "Close" in spy_df.columns:
        spy_df = spy_df.rename(columns={"Close": "SPY_Close"})

    df = df.merge(
        spy_df[["Date", "SPY_Close"]],
        on="Date",
        how="inner"
    )
    df = df.reset_index(drop=True)

    if strategy_name == "momentum":
        window = strategy_params.get("window", 20)
        df = generate_momentum_signal(df, window=window)
        params_used = {"window": window}

    elif strategy_name == "mean_reversion":
        window = strategy_params.get("window", 20)
        threshold = strategy_params.get("threshold", 2)
        df = generate_mean_reversion_signal(df, window=window, threshold=threshold)
        params_used = {"window": window, "threshold": threshold}

    elif strategy_name == "rsi":
        window = strategy_params.get("window", 14)
        overbought = strategy_params.get("overbought", 70)
        oversold = strategy_params.get("oversold", 30)
        df = generate_rsi_signal(df, window=window, overbought=overbought, oversold=oversold)
        params_used = {"window": window, "overbought": overbought, "oversold": oversold}

    elif strategy_name == "macd":
        fast = strategy_params.get("fast", 12)
        slow = strategy_params.get("slow", 26)
        signal_window = strategy_params.get("signal_window", 9)
        df = generate_macd_signal(df, fast=fast, slow=slow, signal_window=signal_window)
        params_used = {"fast": fast, "slow": slow, "signal_window": signal_window}

    elif strategy_name == "bollinger_bands":
        window = strategy_params.get("window", 20)
        num_std = strategy_params.get("num_std", 2)
        df = generate_bollinger_bands_signal(df, window=window, num_std=num_std)
        params_used = {"window": window, "num_std": num_std}

    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    portfolio = Portfolio(initial_cash=initial_cash)
    portfolio_values = []
    positions = []
    trade_actions = []
    execution_signals = []

    for i in range(len(df)):
        price = df.loc[i, "Close"]

        if i == 0:
            signal = 0
        else:
            signal = df.loc[i - 1, "signal"]

        execution_signals.append(signal)

        if signal == 1 and portfolio.shares == 0:
            execute_buy(portfolio, price)
            trade_action = 1
        elif signal == -1 and portfolio.shares > 0:
            execute_sell(portfolio, price)
            trade_action = -1
        else:
            trade_action = 0

        portfolio_value = portfolio.total_value(price)
        portfolio_values.append(portfolio_value)
        positions.append(portfolio.shares)
        trade_actions.append(trade_action)

    df["position"] = positions
    df["trade_action"] = trade_actions
    df["execution_signal"] = execution_signals
    df["portfolio_value"] = portfolio_values
    df["strategy_returns"] = df["portfolio_value"].pct_change()

    report = generate_strategy_report(df, df["SPY_Close"])

    final_value = df["portfolio_value"].iloc[-1]
    total_return = ((final_value / initial_cash) - 1) * 100

    return {
        "df": df,
        "report": report,
        "initial_cash": initial_cash,
        "final_value": final_value,
        "total_return": total_return,
        "params_used": params_used,
    }
