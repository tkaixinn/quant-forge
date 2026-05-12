import pandas as pd
import pathlib
import yfinance as yf


def _find_file_by_normalized_name(base_dir: pathlib.Path, filename: str):
    """Try to find a file in base_dir that matches filename ignoring whitespace and case."""
    def norm(s: str) -> str:
        return "".join(s.split()).lower()

    target = norm(filename)

    for p in base_dir.iterdir():
        if p.is_file() and norm(p.name) == target:
            return p

    return None


def _download_and_cache_ticker(base_dir: pathlib.Path, ticker: str):
    """Download ticker data from yfinance and cache it as a CSV."""
    data = yf.download(
        ticker,
        period="10y",
        auto_adjust=False,
        progress=False,
    )

    if data.empty:
        raise FileNotFoundError(f"No downloadable data found for ticker: {ticker}")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.dropna().reset_index()

    # Cache for later use
    cache_path = base_dir / f"{ticker.upper()}.csv"
    data.to_csv(cache_path, index=False)

    return cache_path


def load_csv(filename: str, start_date: str = None, end_date: str = None):
    base_dir = pathlib.Path(__file__).resolve().parent

    # sanitize user input
    filename = filename.strip()
    filename = filename.strip('"\'')

    path = base_dir / filename

    if not path.exists():
   
        if pathlib.Path(filename).suffix == "":
            path = base_dir / (filename + ".csv")

    if not path.exists():

        found = _find_file_by_normalized_name(base_dir, filename)
        if found is not None:
            path = found

    if not path.exists():

        ticker = pathlib.Path(filename).stem.upper()
        path = _download_and_cache_ticker(base_dir, ticker)

    if not path.exists():
        files = ", ".join([f.name for f in base_dir.iterdir() if f.is_file()])
        raise FileNotFoundError(
            f"CSV not found in data folder: {base_dir/filename}. Available files: {files}"
        )

    df = pd.read_csv(path)

    if "Date" not in df.columns:
        df = df.rename(columns={df.columns[0]: "Date"})

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    
    # Filter by date range if provided
    if start_date is not None:
        df = df[df["Date"] >= pd.to_datetime(start_date)]
    if end_date is not None:
        df = df[df["Date"] <= pd.to_datetime(end_date)]

    required = ["Date", "Open", "High", "Low", "Close", "Volume"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    return df, path