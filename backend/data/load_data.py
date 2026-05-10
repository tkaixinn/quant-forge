import pandas as pd
import pathlib


def _find_file_by_normalized_name(base_dir: pathlib.Path, filename: str):
    """Try to find a file in base_dir that matches filename ignoring whitespace and case."""
    def norm(s: str) -> str:
        return "".join(s.split()).lower()

    target = norm(filename)

    for p in base_dir.iterdir():
        if p.is_file() and norm(p.name) == target:
            return p

    return None


def load_csv(filename: str):
    base_dir = pathlib.Path(__file__).resolve().parent

    # sanitize user input
    filename = filename.strip()
    filename = filename.strip('"\'')

    path = base_dir / filename

    # try a few common fallbacks if exact path not found
    if not path.exists():
        # try adding .csv if user omitted extension
        if pathlib.Path(filename).suffix == "":
            path = base_dir / (filename + ".csv")

    if not path.exists():
        # try to find by matching names ignoring whitespace/case
        found = _find_file_by_normalized_name(base_dir, filename)
        if found is not None:
            path = found

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

    required = ["Date", "Open", "High", "Low", "Close", "Volume"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    return df, path