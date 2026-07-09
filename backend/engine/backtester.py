import pandas as pd
import pathlib
import sys

sys.path.insert(
    0,
    str(pathlib.Path(__file__).resolve().parents[1])
)

from strategies.strategies import (
    generate_momentum_signal,
    generate_mean_reversion_signal
)

from engine.portfolio import Portfolio

from engine.execution import (
    execute_buy,
    execute_sell
)

from load_data import load_csv


filename = input("Enter CSV filename: ")

df, resolved_path = load_csv(filename)

strategy = input(
    "Choose strategy (momentum / mean_reversion): "
)


if strategy == "momentum":

    df = generate_momentum_signal(df)

elif strategy == "mean_reversion":

    df = generate_mean_reversion_signal(df)

else:

    raise ValueError("Invalid strategy selected")


portfolio = Portfolio(initial_cash=10000)

portfolio_values = []
positions = []


for i in range(len(df)):

    price = df.loc[i, "Close"]

    # prevent lookahead bias
    if i == 0:
        signal = 0
    else:
        signal = df.loc[i - 1, "signal"]

    # BUY
    if signal == 1 and portfolio.shares == 0:

        execute_buy(portfolio, price)

    # SELL
    elif signal == -1 and portfolio.shares > 0:

        execute_sell(portfolio, price)

    # TRACK PORTFOLIO
    portfolio_value = (
        portfolio.total_value(price)
    )

    portfolio_values.append(portfolio_value)

    positions.append(portfolio.shares)


df["position"] = positions

df["portfolio_value"] = portfolio_values

df["strategy_returns"] = (
    df["portfolio_value"].pct_change()
)


print(df[[
    "Date",
    "Close",
    "signal",
    "position",
    "portfolio_value"
]].head(20))

print(
    "\nFinal Portfolio Value:",
    round(df["portfolio_value"].iloc[-1], 2)
)

total_return = (
    (
        df["portfolio_value"].iloc[-1]
        / 10000
    ) - 1
) * 100

print(
    "Total Return:",
    round(total_return, 2),
    "%"
)


output_file = (
    resolved_path.parent /
    f"backtest_{resolved_path.name}"
)

df.to_csv(output_file, index=False)

print(f"\nBacktest saved to {output_file}")