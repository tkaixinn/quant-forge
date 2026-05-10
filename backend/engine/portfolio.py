class Portfolio:

    def __init__(self, initial_cash=10000):

        self.cash = initial_cash
        self.shares = 0

    def total_value(self, current_price):

        return self.cash + (self.shares * current_price)
    