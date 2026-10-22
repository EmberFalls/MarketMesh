# MarketMesh

**A Discrete Mathematics-Based Stock Market Network Analyzer**

MarketMesh turns selected stock closing-price series into a graph by calculating daily returns, comparing Pearson correlations, and adding an undirected edge when a selected threshold is met. It then demonstrates graph theory, recurrence relations, generating functions, and modular arithmetic in one classroom application.

This is an educational discrete mathematics project. It does not predict prices, provide trading recommendations, optimize portfolios, or connect to a brokerage. Included CSV files contain historical NSE data; separately generated examples in `data/synthetic-demo/` are synthetic and labeled as such.

## Problem statement

Financial markets contain securities whose historical movements may exhibit stronger or weaker relationships. Modeling selected stocks as vertices and sufficiently strong historical return relationships as edges makes the structure visible and allows graph-theoretic analysis. Recurrence relations, generating functions, and modular arithmetic extend the exploration to discrete sequences, graph walks, and simulated repeating cycles.

## Objective

Demonstrate how discrete mathematics concepts can be applied to stock relationship data: construct a relationship graph, analyze its structure, count walks, represent walk sequences with generating polynomials, simulate recurrence relations, and solve cycle-alignment congruences with the Chinese Remainder Theorem.

## Syllabus mapping

| Unit | Topics | MarketMesh feature |
| --- | --- | --- |
| 4 | Recurrence relations, homogeneous and non-homogeneous examples, Fibonacci, generating functions, counting | Recurrence Lab, walk counting through adjacency powers, truncated ordinary generating polynomial |
| 5 | Divisibility, Euclidean and extended Euclidean algorithms, inverse, primes, factorization, Euler phi, Fermat, congruences, CRT | Modular Cycle Analyzer |
| 6 | Graph representations, degree, components, paths, cycles, Euler/Hamiltonian properties, trees, bipartite graphs | Graph Analysis, sector graph, and Stress Test |

## Architecture

- `marketmesh/data_manager.py`: CSV discovery, cleaning, date alignment, and daily returns.
- `marketmesh/relationship.py`: Pearson correlations and threshold rules.
- `marketmesh/graph_engine.py`: graph construction, adjacency and incidence matrices.
- `marketmesh/graph_algorithms.py`: BFS, DFS, paths, cycles, Euler checks, Hamiltonian backtracking, trees, bipartite coloring.
- `marketmesh/walk_analysis.py` and `generating_function.py`: binary adjacency powers, walk sequences, finite generating polynomials.
- `marketmesh/recurrence.py`: second-order linear recurrence simulator.
- `marketmesh/modular.py`: Euclid, extended Euclid, inverse, primes, phi, Fermat, congruences, and CRT.
- `marketmesh/stress_test.py`: vertex and edge removal comparisons.
- `app.py`: Streamlit user interface and interactive graph visualization.

## Setup

Python 3.11 or newer is recommended.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Choose stocks, date range, and correlation threshold in the sidebar. Pages cover the graph dashboard, graph algorithms and matrices, walk counts and generating functions, recurrence simulation, modular arithmetic and CRT, graph stress tests, and math explanations.

## Data format

Each CSV in `data/` requires a date and close-price column; common NSE headings such as `Date` / `Close Price` and `CH_TIMESTAMP` / `CLOSE_PRICE` are accepted. The included ticker files are real NSE EQ-series daily close prices for January–March 2024. Refresh them from the [NSE Security-wise Archives](https://www.nseindia.com/report-detail/eq_security) with `python scripts/fetch_nse_history.py`; check NSE's current data terms before redistribution. Synthetic educational examples can be regenerated separately with `python generate_demo_data.py` into `data/synthetic-demo/`. To use other real data, upload CSVs in the app sidebar. The filename (without `.csv`) is used as the symbol; uploaded files override local files with matching names. MarketMesh aligns selected series on common dates and calculates percentage returns before correlation.

## Mathematical notes

- Correlation threshold is adjustable and is not a universal definition of a relationship.
- Graph walk counts use the **binary** adjacency matrix, never correlation weights.
- Hamiltonian search uses exact backtracking and is limited to 12 vertices.
- Generating functions derived from finite walk samples are truncated polynomials, not claimed rational closed forms.
- CRT currently requires pairwise-coprime moduli.
- The cycle analyzer models simulated periodic constraints; it does not identify or forecast market cycles.

## Tests

Install the requirements and run:

```bash
pytest
```

The unit tests cover CSV cleaning and alignment, graph algorithms, walk counts, recurrence generation, and modular arithmetic examples.

## Future extensions

Rolling correlation networks, directed lagged relationships, weighted path analysis, centrality measures, live data providers, and exportable reports can be considered after the core educational application.
