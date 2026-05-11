import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from data.load_data import load_csv
from engine.optimizer import (
    optimize_momentum,
    optimize_mean_reversion,
    optimize_rsi,
    optimize_macd,
    optimize_bollinger_bands,
    print_optimization_results,
    export_results_to_csv,
)


def parse_range(range_str):
    """Parse 'min-max' format into tuple (min, max)."""
    parts = range_str.split("-")
    if len(parts) != 2:
        raise ValueError(f"Invalid range format: {range_str}. Use 'min-max'")
    try:
        return (int(parts[0]), int(parts[1]))
    except ValueError:
        return (float(parts[0]), float(parts[1]))


def main():
    parser = argparse.ArgumentParser(
        description="Optimize trading strategy parameters by backtesting combinations."
    )
    parser.add_argument("ticker", help="Stock ticker symbol (or CSV filename)")
    parser.add_argument(
        "strategy",
        choices=["momentum", "mean_reversion", "rsi", "macd", "bollinger_bands"],
        help="Strategy to optimize"
    )
    parser.add_argument(
        "--window-range",
        default="10-50",
        help="Window parameter range as 'min-max' (default: 10-50)"
    )
    parser.add_argument(
        "--window-step",
        type=int,
        default=5,
        help="Step size for window sweep (default: 5)"
    )
    parser.add_argument(
        "--threshold-range",
        default="1-3",
        help="Threshold parameter range as 'min-max' (for mean_reversion, default: 1-3)"
    )
    parser.add_argument(
        "--threshold-step",
        type=float,
        default=0.5,
        help="Step size for threshold sweep (for mean_reversion, default: 0.5)"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of top results to display (default: 5)"
    )
    parser.add_argument(
        "--export",
        help="Export results to CSV file"
    )

    args = parser.parse_args()

    print(f"Loading data for {args.ticker}...")
    try:
        df, resolved_path = load_csv(args.ticker)
    except FileNotFoundError:
        print(f"Error: Could not find {args.ticker}")
        sys.exit(1)

    # Dispatch to appropriate optimizer based on strategy
    if args.strategy == "momentum":
        window_range = parse_range(args.window_range)
        results = optimize_momentum(
            df,
            window_range=window_range,
            step=args.window_step
        )
    
    elif args.strategy == "mean_reversion":
        window_range = parse_range(args.window_range)
        threshold_range = parse_range(args.threshold_range)
        results = optimize_mean_reversion(
            df,
            window_range=window_range,
            threshold_range=threshold_range,
            window_step=args.window_step,
            threshold_step=args.threshold_step
        )
    
    elif args.strategy == "rsi":
        window_range = parse_range(args.window_range)
        results = optimize_rsi(
            df,
            window_range=window_range,
            window_step=args.window_step
        )
    
    elif args.strategy == "macd":
        # For MACD, window_range can be reused for fast parameter
        fast_range = parse_range(args.window_range)
        results = optimize_macd(df, fast_range=fast_range)
    
    elif args.strategy == "bollinger_bands":
        window_range = parse_range(args.window_range)
        results = optimize_bollinger_bands(
            df,
            window_range=window_range,
            window_step=args.window_step
        )
    
    else:
        print(f"Unknown strategy: {args.strategy}")
        sys.exit(1)

    if not results:
        print("No valid results found.")
        sys.exit(1)

    print_optimization_results(results, top_n=args.top_n)

    if args.export:
        export_results_to_csv(results, args.export)

    print("\n✓ Optimization complete!")


if __name__ == "__main__":
    main()
