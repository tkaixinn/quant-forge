import pandas as pd
import pathlib
import sys
import yfinance as yf

sys.path.insert(
    0,
    str(pathlib.Path(__file__).resolve().parents[1])
)

from analysis.report import generate_strategy_report

from strategies.strategies import (
    generate_momentum_signal,
    generate_mean_reversion_signal
)

from engine.portfolio import Portfolio

from engine.execution import (
    execute_buy,
    execute_sell
)

from data.load_data import load_csv


filename = input("Enter CSV filename (strategy asset): ")
df, resolved_path = load_csv(filename)

spy_df = yf.download("SPY", start=df["Date"].iloc[0], end=df["Date"].iloc[-1])
spy_df = spy_df.reset_index()
# yfinance can return MultiIndex columns when downloading with tickers;
# flatten them to single-level names like Close_SPY so merges work predictably
if isinstance(spy_df.columns, pd.MultiIndex):
    new_cols = []
    for col in spy_df.columns.values:
        if isinstance(col, tuple):
            parts = [str(c) for c in col if c and str(c).strip()]
            new_cols.append("_".join(parts))
        else:
            new_cols.append(str(col))
    spy_df.columns = new_cols

# prefer a single-column named SPY_Close for downstream use
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

strategy = input("Choose strategy (momentum / mean_reversion): ")

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

    if i == 0:
        signal = 0
    else:
        signal = df.loc[i - 1, "signal"]

    if signal == 1 and portfolio.shares == 0:
        execute_buy(portfolio, price)

    elif signal == -1 and portfolio.shares > 0:
        execute_sell(portfolio, price)

    portfolio_value = portfolio.total_value(price)

    portfolio_values.append(portfolio_value)
    positions.append(portfolio.shares)


df["position"] = positions
df["portfolio_value"] = portfolio_values
df["strategy_returns"] = df["portfolio_value"].pct_change()

print("\nFinal Portfolio Value:", df["portfolio_value"].iloc[-1])
print("Total Return:", ((df["portfolio_value"].iloc[-1] / 10000) - 1) * 100, "%")

output_file = resolved_path.parent / f"backtest_{resolved_path.name}"
df.to_csv(output_file, index=False)

print(f"\nBacktest saved to {output_file}")

report = generate_strategy_report(df, df["SPY_Close"])

print("\n====================")
print("STRATEGY REPORT (ALIGNED)")
print("====================")

print("\n--- Strategy Metrics ---")
for k, v in report["strategy_metrics"].items():
    print(f"{k}: {round(v, 4)}")

print("\n--- Benchmark (SPY) ---")
for k, v in report["benchmark_metrics"].items():
    print(f"{k}: {round(v, 4)}")

print("\n--- Alpha vs Market ---")
print(round(report["alpha_vs_market"], 4))