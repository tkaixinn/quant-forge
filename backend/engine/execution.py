TRANSACTION_COST_RATE = 0.001


def execute_buy(portfolio, price):

    transaction_cost = (
        portfolio.cash * TRANSACTION_COST_RATE
    )

    available_cash = (
        portfolio.cash - transaction_cost
    )

    portfolio.shares = (
        available_cash / price
    )

    portfolio.cash = 0


def execute_sell(portfolio, price):

    proceeds = portfolio.shares * price

    transaction_cost = (
        proceeds * TRANSACTION_COST_RATE
    )

    portfolio.cash = (
        proceeds - transaction_cost
    )

    portfolio.shares = 0
