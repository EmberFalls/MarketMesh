# Market data

The ten root-level ticker CSV files contain NSE EQ-series daily close prices from January 1 to March 29, 2024, retrieved on October 3, 2026, from NSE's official [Security-wise Archives](https://www.nseindia.com/report-detail/eq_security) CSV export. Values use the archive's unadjusted `Close Price` field and are stored as `Date,Close` for MarketMesh. Consult the source's current terms before redistribution.

The app also accepts multiple CSV uploads in the sidebar. It recognizes common exchange headers such as `Date` / `Close Price` and `CH_TIMESTAMP` / `CLOSE_PRICE`; the filename (without `.csv`) becomes the symbol. The generated synthetic examples live separately under `synthetic-demo/` and can be recreated with `python generate_demo_data.py`.
