import pathlib
import sys
import socket
from datetime import date

from flask import Flask, jsonify, request
import pandas as pd
from flask_cors import CORS
import os

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from data.load_data import load_csv
from engine.backtest_core import run_backtest
from engine.optimizer import (
    optimize_momentum,
    optimize_mean_reversion,
    optimize_rsi,
    optimize_macd,
    optimize_bollinger_bands,
)

app = Flask(__name__)
CORS(app)


if __name__ == "__main__":
    # When app.py is executed directly, honor PORT env var (default 5002)
    port = int(os.getenv("PORT", "5002"))
    app.run(host="0.0.0.0", port=port, debug=True)

AVAILABLE_STRATEGIES = [
    {
        "name": "momentum",
        "description": "Buy when recent price momentum is positive.",
    },
    {
        "name": "mean_reversion",
        "description": "Buy when z-score is low and sell when it is high.",
    },
    {
        "name": "rsi",
        "description": "Buy when RSI is oversold and sell when overbought.",
    },
    {
        "name": "macd",
        "description": "Trade MACD crossovers.",
    },
    {
        "name": "bollinger_bands",
        "description": "Buy below lower band and sell above upper band.",
    },
]


@app.get("/")
def index():
    return jsonify(
        {
            "name": "quant-forge API",
            "status": "running",
            "routes": ["/health", "/strategies", "/backtest", "/optimize"],
        }
    )


def _parse_range(value, default_type=int):
    """Accept either [min, max] or 'min-max' and return a tuple."""
    if value is None:
        return None

    if isinstance(value, (list, tuple)):
        if len(value) != 2:
            raise ValueError("Range must contain exactly two values")
        return default_type(value[0]), default_type(value[1])

    if isinstance(value, str):
        parts = value.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid range format: {value}")
        return default_type(parts[0]), default_type(parts[1])

    raise ValueError(f"Unsupported range value: {value}")


def _json_error(message, status_code=400):
    return jsonify({"error": message}), status_code


def _port_is_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def _select_local_port(preferred_port=5000):
    for port in range(preferred_port, preferred_port + 11):
        if _port_is_available(port):
            return port
    raise RuntimeError(f"No available local port found starting at {preferred_port}")


def _serialize_chart_data(df):
    """Return a compact chart-friendly slice of the backtest dataframe."""
    columns = ["Date", "Close", "signal", "execution_signal", "trade_action", "position", "portfolio_value", "SPY_Close"]
    available = [col for col in columns if col in df.columns]

    chart_df = df[available].copy()

    if "SPY_Close" in chart_df.columns and "portfolio_value" in chart_df.columns and not chart_df.empty:
        spy_start = chart_df["SPY_Close"].iloc[0]
        strategy_start = chart_df["portfolio_value"].iloc[0]
        if spy_start and spy_start != 0:
            chart_df["SPY_Portfolio_Value"] = (chart_df["SPY_Close"] / spy_start) * strategy_start

    if "Date" in chart_df.columns:
        chart_df["Date"] = chart_df["Date"].astype(str)

    return chart_df.to_dict(orient="records")


def _serialize_benchmark_metrics(report, df):
    benchmark = report.get("benchmark_metrics", {})

    benchmark_total_return = 0.0
    if "SPY_Close" in df.columns and not df.empty:
        spy_start = df["SPY_Close"].iloc[0]
        spy_end = df["SPY_Close"].iloc[-1]
        if spy_start and spy_start != 0:
            benchmark_total_return = ((spy_end / spy_start) - 1) * 100

    return {
        "sharpe_ratio": benchmark.get("benchmark_sharpe", 0.0),
        "max_drawdown": benchmark.get("benchmark_max_drawdown", 0.0),
        "cagr": benchmark.get("benchmark_cagr", 0.0),
        "win_rate": benchmark.get("benchmark_win_rate", 0.0),
        "profit_factor": benchmark.get("benchmark_profit_factor", 0.0),
        "total_return": benchmark_total_return,
    }


def _serialize_backtest_result(result, ticker, strategy):
    report = result["report"]
    df = result["df"]
    return {
        "ticker": ticker,
        "strategy": strategy,
        "params_used": result["params_used"],
        "initial_cash": result.get("initial_cash", 10000),
        "final_value": result["final_value"],
        "total_return": result["total_return"],
        "metrics": report["strategy_metrics"],
        "benchmark_metrics": _serialize_benchmark_metrics(report, df),
        "alpha_vs_market": report["alpha_vs_market"],
        "chart_data": _serialize_chart_data(df),
        "generated_at": date.today().isoformat(),
    }


def _serialize_optimization_result(result, ticker, strategy):
    report = result["report"]
    df = result["df"]
    return {
        "ticker": ticker,
        "strategy": strategy,
        "params_used": result["params_used"],
        "initial_cash": result.get("initial_cash", 10000),
        "final_value": result["final_value"],
        "total_return": result["total_return"],
        "metrics": report["strategy_metrics"],
        "benchmark_metrics": _serialize_benchmark_metrics(report, df),
        "alpha_vs_market": report["alpha_vs_market"],
    }


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/strategies")
def list_strategies():
    return jsonify({"strategies": AVAILABLE_STRATEGIES})


@app.get("/data_range")
def data_range():
    """Return the earliest and latest available dates for a ticker's data.

    Query params: ?ticker=MSFT
    """
    ticker = request.args.get("ticker")
    if not ticker:
        return _json_error("'ticker' query parameter is required")

    try:
        df, _ = load_csv(ticker)
        if df.empty:
            return _json_error("No data available for ticker", 404)

        earliest = df["Date"].min()
        latest = df["Date"].max()

        return jsonify({
            "ticker": ticker,
            "earliest": pd.to_datetime(earliest).date().isoformat(),
            "latest": pd.to_datetime(latest).date().isoformat(),
        })
    except FileNotFoundError:
        return _json_error(f"Could not find data for '{ticker}'", 404)
    except Exception as exc:
        return _json_error(str(exc), 500)


@app.post("/backtest")
def backtest():
    payload = request.get_json(silent=True) or {}
    ticker = payload.get("ticker")
    strategy = payload.get("strategy")
    strategy_params = payload.get("params", {})
    benchmark_ticker = payload.get("benchmark_ticker", "SPY")
    initial_cash = float(payload.get("initial_cash", 10000))
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")

    if not ticker:
        return _json_error("'ticker' is required")
    if not strategy:
        return _json_error("'strategy' is required")

    try:
        df, _ = load_csv(ticker, start_date=start_date, end_date=end_date)
        result = run_backtest(
            df,
            strategy_name=strategy,
            initial_cash=initial_cash,
            strategy_params=strategy_params,
            benchmark_ticker=benchmark_ticker,
        )
        return jsonify(_serialize_backtest_result(result, ticker, strategy))
    except FileNotFoundError:
        return _json_error(f"Could not find data for '{ticker}'", 404)
    except ValueError as exc:
        return _json_error(str(exc))
    except Exception as exc:
        return _json_error(f"Backtest failed: {exc}", 500)


@app.post("/optimize")
def optimize():
    payload = request.get_json(silent=True) or {}
    ticker = payload.get("ticker")
    strategy = payload.get("strategy")
    top_n = int(payload.get("top_n", 5))
    export_path = payload.get("export_path")
    initial_cash = float(payload.get("initial_cash", 10000))
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")

    if not ticker:
        return _json_error("'ticker' is required")
    if not strategy:
        return _json_error("'strategy' is required")

    try:
        df, _ = load_csv(ticker, start_date=start_date, end_date=end_date)

        if strategy == "momentum":
            window_range = _parse_range(payload.get("window_range", [10, 50]))
            step = int(payload.get("window_step", 5))
            results = optimize_momentum(
                df,
                window_range=window_range,
                step=step,
                initial_cash=initial_cash,
            )

        elif strategy == "mean_reversion":
            window_range = _parse_range(payload.get("window_range", [10, 50]))
            threshold_range = _parse_range(payload.get("threshold_range", [1, 3]), default_type=float)
            window_step = int(payload.get("window_step", 5))
            threshold_step = float(payload.get("threshold_step", 0.5))
            results = optimize_mean_reversion(
                df,
                window_range=window_range,
                threshold_range=threshold_range,
                window_step=window_step,
                threshold_step=threshold_step,
                initial_cash=initial_cash,
            )

        elif strategy == "rsi":
            window_range = _parse_range(payload.get("window_range", [5, 30]))
            window_step = int(payload.get("window_step", 5))
            results = optimize_rsi(
                df,
                window_range=window_range,
                window_step=window_step,
                initial_cash=initial_cash,
            )

        elif strategy == "macd":
            fast_range = _parse_range(payload.get("fast_range", [5, 20]))
            slow_range = _parse_range(payload.get("slow_range", [20, 35]))
            signal_range = _parse_range(payload.get("signal_range", [5, 15]))
            fast_step = int(payload.get("fast_step", 3))
            slow_step = int(payload.get("slow_step", 3))
            signal_step = int(payload.get("signal_step", 2))
            results = optimize_macd(
                df,
                fast_range=fast_range,
                slow_range=slow_range,
                signal_range=signal_range,
                fast_step=fast_step,
                slow_step=slow_step,
                signal_step=signal_step,
                initial_cash=initial_cash,
            )

        elif strategy == "bollinger_bands":
            window_range = _parse_range(payload.get("window_range", [10, 30]))
            window_step = int(payload.get("window_step", 5))
            num_std = float(payload.get("num_std", 2))
            results = optimize_bollinger_bands(
                df,
                window_range=window_range,
                window_step=window_step,
                num_std=num_std,
                initial_cash=initial_cash,
            )

        else:
            return _json_error(f"Unknown strategy: {strategy}")

        if not results:
            return _json_error("No valid optimization results found", 400)

        serialized_results = [
            _serialize_optimization_result(result, ticker, strategy)
            for result in results[:top_n]
        ]

        response = {
            "ticker": ticker,
            "strategy": strategy,
            "initial_cash": initial_cash,
            "top_n": top_n,
            "top_results": serialized_results,
            "count": len(results),
        }

        if export_path:
            # If requested, export the full result set to CSV using the existing engine helper.
            from engine.optimizer import export_results_to_csv

            export_results_to_csv(results, export_path)
            response["exported_to"] = export_path

        return jsonify(response)

    except FileNotFoundError:
        return _json_error(f"Could not find data for '{ticker}'", 404)
    except ValueError as exc:
        return _json_error(str(exc))
    except Exception as exc:
        return _json_error(f"Optimization failed: {exc}", 500)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT") or _select_local_port(5000))
    app.run(host="0.0.0.0", port=port, debug=False)
