from data.load_data import load_csv

from strategies.strategies import (
    generate_momentum_signal,
    generate_mean_reversion_signal
)

filename = input("Enter CSV filename (e.g. MSFT.csv): ").upper()

df, resolved_path = load_csv(filename)

strategy = input("Choose strategy (momentum / mean_reversion): ")

if strategy == "momentum":
    df = generate_momentum_signal(df)

elif strategy == "mean_reversion":
    df = generate_mean_reversion_signal(df)

else:
    raise ValueError("Invalid strategy selected")

print(df[["Close", "signal"]].head())

output_file = resolved_path.parent / f"signals_{resolved_path.name}"
df.to_csv(output_file, index=False)

print(f"Signals saved to {output_file}")