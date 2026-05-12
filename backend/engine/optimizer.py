import pandas as pd
import sys
import pathlib
from itertools import product

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from data.load_data import load_csv
from engine.backtest_core import run_backtest


def optimize_momentum(df, window_range=(10, 50), step=5, initial_cash=10000):

    results = []
    min_window, max_window = window_range
    windows = range(min_window, max_window + 1, step)
    
    print(f"\nOptimizing momentum strategy: windows {list(windows)}")
    
    for i, window in enumerate(windows):
        print(f"  [{i+1}/{len(list(windows))}] Testing window={window}...", end=" ", flush=True)
        
        try:
            result = run_backtest(
                df,
                strategy_name="momentum",
                initial_cash=initial_cash,
                strategy_params={"window": window}
            )
            
            result["window"] = window
            results.append(result)
            print(f"Sharpe: {result['report']['strategy_metrics']['sharpe_ratio']:.4f}")
        except Exception as e:
            print(f"Failed: {e}")
    
    results.sort(
        key=lambda x: x["report"]["strategy_metrics"]["sharpe_ratio"],
        reverse=True
    )
    
    return results


def optimize_mean_reversion(df, window_range=(10, 50), threshold_range=(1, 3), 
                            window_step=5, threshold_step=0.5, initial_cash=10000):
  
    results = []
    min_window, max_window = window_range
    min_threshold, max_threshold = threshold_range
    
    windows = list(range(min_window, max_window + 1, window_step))

    thresholds = [round(min_threshold + i * threshold_step, 1) 
                  for i in range(int((max_threshold - min_threshold) / threshold_step) + 1)]
    
    total = len(windows) * len(thresholds)
    print(f"\nOptimizing mean reversion strategy: {total} combinations")
    print(f"  Windows: {windows}")
    print(f"  Thresholds: {thresholds}")
    
    count = 0
    for window, threshold in product(windows, thresholds):
        count += 1
        print(f"  [{count}/{total}] window={window}, threshold={threshold}...", end=" ", flush=True)
        
        try:
            result = run_backtest(
                df,
                strategy_name="mean_reversion",
                initial_cash=initial_cash,
                strategy_params={"window": window, "threshold": threshold}
            )
            
            result["window"] = window
            result["threshold"] = threshold
            results.append(result)
            print(f"Sharpe: {result['report']['strategy_metrics']['sharpe_ratio']:.4f}")
        except Exception as e:
            print(f"Failed: {e}")
    
    results.sort(
        key=lambda x: x["report"]["strategy_metrics"]["sharpe_ratio"],
        reverse=True
    )
    
    return results


def print_optimization_results(results, top_n=5):
    """Print top N optimization results in a readable format."""
    print("\n" + "="*80)
    print(f"TOP {min(top_n, len(results))} RESULTS (sorted by Sharpe Ratio)")
    print("="*80)
    
    for rank, result in enumerate(results[:top_n], 1):
        params = result.get("params_used", {})
        metrics = result["report"]["strategy_metrics"]
        
        print(f"\n#{rank}")
        print(f"  Params: {params}")
        print(f"  Final Value: ${result['final_value']:.2f}")
        print(f"  Total Return: {result['total_return']:.2f}%")
        print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
        print(f"  CAGR: {metrics['cagr']:.4f}")
        print(f"  Max Drawdown: {metrics['max_drawdown']:.4f}")
        print(f"  Win Rate: {metrics['win_rate']:.4f}")
        print(f"  Profit Factor: {metrics['profit_factor']:.4f}")


def export_results_to_csv(results, output_path):
    data = []
    for result in results:
        params = result.get("params_used", {})
        metrics = result["report"]["strategy_metrics"]
        benchmark = result["report"]["benchmark_metrics"]
        
        row = {
            "final_value": result["final_value"],
            "total_return": result["total_return"],
            "sharpe_ratio": metrics["sharpe_ratio"],
            "cagr": metrics["cagr"],
            "max_drawdown": metrics["max_drawdown"],
            "win_rate": metrics["win_rate"],
            "profit_factor": metrics["profit_factor"],
            "alpha_vs_market": result["report"]["alpha_vs_market"],
            "benchmark_sharpe": benchmark["benchmark_sharpe"],
            "benchmark_cagr": benchmark["benchmark_cagr"],
        }
        row.update(params)  
        data.append(row)
    
    results_df = pd.DataFrame(data)
    results_df.to_csv(output_path, index=False)
    print(f"\nResults exported to {output_path}")
    
    return results_df


def optimize_rsi(df, window_range=(5, 30), window_step=5, overbought=70, oversold=30, initial_cash=10000):
    results = []
    min_window, max_window = window_range
    windows = range(min_window, max_window + 1, window_step)
    
    print(f"\nOptimizing RSI strategy: windows {list(windows)}")
    
    for i, window in enumerate(windows):
        print(f"  [{i+1}/{len(list(windows))}] Testing window={window}...", end=" ", flush=True)
        
        try:
            result = run_backtest(
                df,
                strategy_name="rsi",
                initial_cash=initial_cash,
                strategy_params={"window": window, "overbought": overbought, "oversold": oversold}
            )
            
            result["window"] = window
            results.append(result)
            print(f"Sharpe: {result['report']['strategy_metrics']['sharpe_ratio']:.4f}")
        except Exception as e:
            print(f"Failed: {e}")
    
    results.sort(
        key=lambda x: x["report"]["strategy_metrics"]["sharpe_ratio"],
        reverse=True
    )
    
    return results


def optimize_macd(df, fast_range=(5, 20), slow_range=(20, 35), signal_range=(5, 15),
                  fast_step=3, slow_step=3, signal_step=2, initial_cash=10000):
    results = []
    
    fast_vals = list(range(fast_range[0], fast_range[1] + 1, fast_step))
    slow_vals = list(range(slow_range[0], slow_range[1] + 1, slow_step))
    signal_vals = list(range(signal_range[0], signal_range[1] + 1, signal_step))
    
    total = len(fast_vals) * len(slow_vals) * len(signal_vals)
    print(f"\nOptimizing MACD strategy: {total} combinations")
    
    count = 0
    for fast, slow, signal_window in product(fast_vals, slow_vals, signal_vals):
        if fast >= slow: 
            continue
        
        count += 1
        print(f"  [{count}/{total}] fast={fast}, slow={slow}, signal={signal_window}...", end=" ", flush=True)
        
        try:
            result = run_backtest(
                df,
                strategy_name="macd",
                initial_cash=initial_cash,
                strategy_params={"fast": fast, "slow": slow, "signal_window": signal_window}
            )
            
            result["fast"] = fast
            result["slow"] = slow
            result["signal_window"] = signal_window
            results.append(result)
            print(f"Sharpe: {result['report']['strategy_metrics']['sharpe_ratio']:.4f}")
        except Exception as e:
            print(f"Failed: {e}")
    
    results.sort(
        key=lambda x: x["report"]["strategy_metrics"]["sharpe_ratio"],
        reverse=True
    )
    
    return results


def optimize_bollinger_bands(df, window_range=(10, 30), window_step=5, num_std=2, initial_cash=10000):
    results = []
    min_window, max_window = window_range
    windows = range(min_window, max_window + 1, window_step)
    
    print(f"\nOptimizing Bollinger Bands strategy: windows {list(windows)}")
    
    for i, window in enumerate(windows):
        print(f"  [{i+1}/{len(list(windows))}] Testing window={window}...", end=" ", flush=True)
        
        try:
            result = run_backtest(
                df,
                strategy_name="bollinger_bands",
                initial_cash=initial_cash,
                strategy_params={"window": window, "num_std": num_std}
            )
            
            result["window"] = window
            results.append(result)
            print(f"Sharpe: {result['report']['strategy_metrics']['sharpe_ratio']:.4f}")
        except Exception as e:
            print(f"Failed: {e}")
    
    results.sort(
        key=lambda x: x["report"]["strategy_metrics"]["sharpe_ratio"],
        reverse=True
    )
    
    return results
