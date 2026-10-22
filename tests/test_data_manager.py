import pandas as pd

from marketmesh.data_manager import StockDataManager


def test_returns_from_prices():
    prices = pd.DataFrame({"A": [100, 110, 121]})
    returns = StockDataManager.calculate_returns(prices)
    assert list(returns["A"].round(3)) == [0.1, 0.1]


def test_date_filter_and_alignment(tmp_path):
    (tmp_path / "A.csv").write_text("Date,Close\n2024-01-01,100\n2024-01-02,110\n", encoding="utf-8")
    (tmp_path / "B.csv").write_text("Date,Close\n2024-01-02,200\n2024-01-03,220\n", encoding="utf-8")
    prices = StockDataManager(tmp_path).align_close_prices(["A", "B"])
    assert list(prices.index.strftime("%Y-%m-%d")) == ["2024-01-02"]


def test_load_cleans_duplicates_and_bad_rows(tmp_path):
    (tmp_path / "A.csv").write_text("Date,Close\n2024-01-02,110\n2024-01-01,100\n2024-01-02,111\nbad,80\n", encoding="utf-8")
    frame = StockDataManager(tmp_path).load_stock("A")
    assert list(frame["Close"]) == [100, 111]


def test_uploaded_exchange_csv_column_aliases():
    payload = b'CH_TIMESTAMP,CLOSE_PRICE\n02-Jan-2024,"1,000"\n03-Jan-2024,"1,005"\n'
    manager = StockDataManager(uploaded_csvs={"TCS": payload})
    frame = manager.load_stock("TCS")
    assert "TCS" in manager.available_stocks()
    assert list(frame["Close"]) == [1000, 1005]
