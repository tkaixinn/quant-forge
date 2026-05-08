import yfinance as yf

ticker = input("Enter ticker: ").upper()

start_date = input("Start date (YYYY-MM-DD): ")
end_date = input("End date (YYYY-MM-DD): ")

data = yf.download(
    ticker,
    start=start_date,
    end=end_date,
    auto_adjust=False
)

data = data.dropna()

if hasattr(data.columns, "levels"):
    data.columns = data.columns.get_level_values(0)

data = data.reset_index()

filename = f"{ticker}.csv"

data.to_csv(filename, index=False)

print(f"Data saved to {filename}")