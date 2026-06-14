from analysis.metrics import (
    compute_returns,
    compute_trade_returns,
    sharpe_ratio,
    max_drawdown,
    cagr,
    win_rate,
    profit_factor
)


def generate_strategy_report(portfolio_df, benchmark_price_series):

    returns = compute_returns(portfolio_df)
    trade_returns = compute_trade_returns(portfolio_df)
    portfolio_series = portfolio_df["portfolio_value"]

    strategy = {
        "sharpe_ratio": sharpe_ratio(returns),
        "max_drawdown": max_drawdown(portfolio_series),
        "cagr": cagr(portfolio_series),
        "win_rate": win_rate(trade_returns),
        "profit_factor": profit_factor(trade_returns),
    }

    benchmark_returns = benchmark_price_series.pct_change().dropna()

    benchmark = {
        "benchmark_sharpe": sharpe_ratio(benchmark_returns),
        "benchmark_cagr": cagr(benchmark_price_series),
        "benchmark_max_drawdown": max_drawdown(benchmark_price_series),
        "benchmark_win_rate": win_rate(benchmark_returns),
        "benchmark_profit_factor": profit_factor(benchmark_returns),
    }

    alpha = strategy["cagr"] - benchmark["benchmark_cagr"]

    return {
        "strategy_metrics": strategy,
        "benchmark_metrics": benchmark,
        "alpha_vs_market": alpha
    }