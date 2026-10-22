"""Regenerate the reproducible synthetic stock CSVs used in classroom demos."""

import csv
import math
from datetime import date, timedelta
from pathlib import Path


OUTPUT = Path(__file__).parent / "data" / "synthetic-demo"
SYMBOLS = ["TCS", "INFY", "WIPRO", "HCLTECH", "RELIANCE", "HDFCBANK", "ICICIBANK", "AXISBANK", "TATAMOTORS", "M&M"]
BASE = {"TCS": 3500, "INFY": 1450, "WIPRO": 500, "HCLTECH": 1300, "RELIANCE": 2500, "HDFCBANK": 1500, "ICICIBANK": 900, "AXISBANK": 950, "TATAMOTORS": 700, "M&M": 1400}
INDUSTRY = {"TCS": "IT", "INFY": "IT", "WIPRO": "IT", "HCLTECH": "IT", "RELIANCE": "Energy", "HDFCBANK": "Banking", "ICICIBANK": "Banking", "AXISBANK": "Banking", "TATAMOTORS": "Automobile", "M&M": "Automobile"}
PHASE = {"IT": 0.0, "Energy": 1.3, "Banking": 2.7, "Automobile": 4.0}


def main():
    OUTPUT.mkdir(exist_ok=True)
    dates, current = [], date(2024, 1, 1)
    while current <= date(2024, 3, 29):
        if current.weekday() < 5:
            dates.append(current)
        current += timedelta(days=1)
    for index, symbol in enumerate(SYMBOLS):
        price = float(BASE[symbol])
        rows = []
        for day, current_date in enumerate(dates):
            # A modest shared component and a stronger industry component create
            # visible clusters; ticker-specific waves keep return series distinct.
            industry = INDUSTRY[symbol]
            ret = 0.00018 * math.sin(day * 0.23) + 0.0014 * math.sin(day * 0.41 + PHASE[industry])
            ret += 0.00042 * math.sin(day * (0.77 + index * 0.018) + index * 1.19)
            ret += 0.00022 * math.cos(day * 0.91 + index)
            if day:
                price *= 1 + ret
            rows.append((current_date.isoformat(), f"{price:.2f}"))
        with (OUTPUT / f"{symbol}.csv").open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Close"])
            writer.writerows(rows)


if __name__ == "__main__":
    main()
