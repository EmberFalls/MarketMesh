"""Download official NSE security-wise archive CSVs for the classroom dataset.

The NSE archive's public CSV export is used for a small, explicitly bounded
date range. Check NSE's current terms before redistributing downloaded data.
"""

import argparse
import csv
from datetime import datetime
from io import StringIO
from pathlib import Path
import time
from urllib.parse import urlencode

import requests


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data"
SYMBOLS = ["TCS", "INFY", "WIPRO", "HCLTECH", "RELIANCE", "HDFCBANK", "ICICIBANK", "AXISBANK", "TATAMOTORS", "M&M"]
ARCHIVE_PAGE = "https://www.nseindia.com/report-detail/eq_security"
DATA_ENDPOINT = "https://www.nseindia.com/api/historicalOR/generateSecurityWiseHistoricalData"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/csv,application/json,*/*",
    "Referer": ARCHIVE_PAGE,
}


def fetch_symbol(session: requests.Session, symbol: str, start: str, end: str):
    params = {"from": start, "to": end, "symbol": symbol, "type": "priceVolumeDeliverable", "series": "EQ", "csv": "true"}
    response = session.get(f"{DATA_ENDPOINT}?{urlencode(params)}", headers=HEADERS, timeout=30)
    response.raise_for_status()
    text = response.content.decode("utf-8-sig")
    reader = csv.DictReader(StringIO(text))
    rows = []
    for row in reader:
        normalized = {key.strip().lower(): (value or "").strip() for key, value in row.items() if key}
        date_text = normalized.get("date")
        close_text = normalized.get("close price")
        if not date_text or not close_text:
            continue
        trading_date = datetime.strptime(date_text, "%d-%b-%Y").date().isoformat()
        close = float(close_text.replace(",", ""))
        rows.append((trading_date, close))
    rows.sort()
    if len(rows) < 2:
        raise ValueError(f"NSE returned only {len(rows)} usable rows for {symbol}.")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="start", default="01-01-2024", help="Start date in DD-MM-YYYY format")
    parser.add_argument("--to", dest="end", default="29-03-2024", help="End date in DD-MM-YYYY format")
    parser.add_argument("--symbols", nargs="+", default=SYMBOLS, help="NSE equity symbols to download")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)
    with requests.Session() as session:
        landing = session.get(ARCHIVE_PAGE, headers=HEADERS, timeout=30)
        landing.raise_for_status()
        for index, symbol in enumerate(args.symbols):
            rows = fetch_symbol(session, symbol, args.start, args.end)
            destination = OUTPUT_DIR / f"{symbol}.csv"
            with destination.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream)
                writer.writerow(["Date", "Close"])
                writer.writerows(rows)
            print(f"{symbol}: saved {len(rows)} rows to {destination.relative_to(ROOT)}")
            if index + 1 < len(args.symbols):
                time.sleep(0.5)


if __name__ == "__main__":
    main()
