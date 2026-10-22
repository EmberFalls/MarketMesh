"""Load, clean, align, and transform stock price CSV files."""

from pathlib import Path
from typing import Iterable
from io import BytesIO

import pandas as pd


class StockDataManager:
    """Manage CSV files with at least Date and Close columns."""

    def __init__(self, data_dir: str | Path = "data", uploaded_csvs: dict[str, bytes] | None = None) -> None:
        self.data_dir = Path(data_dir)
        self.uploaded_csvs = uploaded_csvs or {}

    def available_stocks(self) -> list[str]:
        """Return symbols represented by CSV files in the data directory."""
        return sorted(set(path.stem for path in self.data_dir.glob("*.csv")) | set(self.uploaded_csvs))

    def load_stock(self, symbol: str) -> pd.DataFrame:
        """Load and normalize one stock file, rejecting malformed inputs."""
        path = self.data_dir / f"{symbol}.csv"
        if symbol in self.uploaded_csvs:
            frame = pd.read_csv(BytesIO(self.uploaded_csvs[symbol]))
        elif path.is_file():
            frame = pd.read_csv(path)
        else:
            raise FileNotFoundError(f"No CSV data found for {symbol} in {self.data_dir}.")
        columns = {str(column).strip().lower(): column for column in frame.columns}
        date_column = next((columns[name] for name in ("date", "timestamp", "ch_timestamp", "trade date", "date1") if name in columns), None)
        close_column = next((columns[name] for name in ("close", "close price", "close_price", "closeprice", "closing price") if name in columns), None)
        if date_column is None or close_column is None:
            raise ValueError(f"{path.name} must contain Date and Close columns.")
        frame = frame.rename(columns={date_column: "Date", close_column: "Close"})
        frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
        close_values = frame["Close"].astype("string").str.replace(",", "", regex=False)
        frame["Close"] = pd.to_numeric(close_values, errors="coerce")
        frame = frame.dropna(subset=["Date", "Close"])
        frame = frame.loc[frame["Close"] > 0].sort_values("Date")
        frame = frame.drop_duplicates(subset="Date", keep="last").set_index("Date")
        return frame

    def load_many(self, symbols: Iterable[str]) -> dict[str, pd.DataFrame]:
        return {symbol: self.load_stock(symbol) for symbol in symbols}

    @staticmethod
    def filter_dates(frame: pd.DataFrame, start_date=None, end_date=None) -> pd.DataFrame:
        result = frame.copy()
        if start_date is not None:
            result = result.loc[result.index >= pd.Timestamp(start_date)]
        if end_date is not None:
            result = result.loc[result.index <= pd.Timestamp(end_date)]
        return result

    def align_close_prices(self, symbols: Iterable[str], start_date=None, end_date=None) -> pd.DataFrame:
        frames = self.load_many(symbols)
        if not frames:
            return pd.DataFrame()
        prices = pd.concat({symbol: frame["Close"] for symbol, frame in frames.items()}, axis=1, join="inner")
        prices = prices.dropna(how="any").sort_index()
        if start_date is not None:
            prices = prices.loc[prices.index >= pd.Timestamp(start_date)]
        if end_date is not None:
            prices = prices.loc[prices.index <= pd.Timestamp(end_date)]
        return prices

    @staticmethod
    def calculate_returns(price_frame: pd.DataFrame) -> pd.DataFrame:
        """Compute percentage daily returns; raw price levels are never compared."""
        return price_frame.pct_change(fill_method=None).dropna(how="any")
