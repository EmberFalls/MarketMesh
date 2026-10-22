"""Streamlit classroom application for MarketMesh."""

from datetime import date
import hashlib
from pathlib import Path

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from marketmesh.data_manager import StockDataManager
from marketmesh.explanations import CONCEPTS
from marketmesh.generating_function import GeneratingFunctionEngine
from marketmesh.graph_algorithms import GraphAlgorithms
from marketmesh.graph_engine import StockGraph
from marketmesh.modular import ModularArithmeticEngine as Modular
from marketmesh.recurrence import RecurrenceSolver
from marketmesh.relationship import RelationshipAnalyzer
from marketmesh.stress_test import GraphStressTester
from marketmesh.walk_analysis import WalkAnalyzer


ROOT = Path(__file__).parent
SECTORS = {
    "TCS": "IT", "INFY": "IT", "WIPRO": "IT", "HCLTECH": "IT",
    "RELIANCE": "Energy", "HDFCBANK": "Banking", "ICICIBANK": "Banking",
    "AXISBANK": "Banking", "TATAMOTORS": "Automobile", "M&M": "Automobile",
}

st.set_page_config(page_title="MarketMesh", page_icon="🕸️", layout="wide")
st.title("MarketMesh")
st.caption("A Discrete Mathematics-Based Stock Market Network Analyzer")
st.info("Included CSVs contain historical NSE data. This application demonstrates historical mathematical analysis, not stock forecasts or financial advice.")

with st.sidebar:
    st.header("Network inputs")
    uploaded_files = st.file_uploader("Add historical CSV files", type=["csv"], accept_multiple_files=True, help="Each file needs Date and Close columns. The filename (without .csv) becomes its stock symbol.")
    uploaded_csvs = {Path(upload.name).stem: upload.getvalue() for upload in uploaded_files}
    manager = StockDataManager(ROOT / "data", uploaded_csvs=uploaded_csvs)
    available = manager.available_stocks()
    if uploaded_csvs:
        st.caption("Uploaded CSVs override local data files with the same filename symbol.")
    if not available:
        st.error("No stock CSV files found or uploaded.")
        st.stop()
    default_config = {"stocks": available[: min(8, len(available))], "start": date(2024, 1, 1), "end": date(2024, 3, 29), "threshold": 0.65, "include_negative": False}
    st.session_state.setdefault("marketmesh_config", default_config)
    current_config = st.session_state["marketmesh_config"]
    with st.form("network_inputs"):
        configured_stocks = [s for s in current_config["stocks"] if s in available]
        input_stocks = st.multiselect("Stocks", available, default=configured_stocks or available[: min(8, len(available))], help="Select at least two stocks with overlapping dates.")
        input_start = st.date_input("Start date", value=current_config["start"])
        input_end = st.date_input("End date", value=current_config["end"])
        input_threshold = st.slider("Correlation threshold", 0.0, 1.0, float(current_config["threshold"]), 0.01)
        input_negative = st.checkbox("Include strong negative correlations", value=current_config["include_negative"])
        build_graph = st.form_submit_button("Build Graph", type="primary")
    if build_graph:
        st.session_state["marketmesh_config"] = {"stocks": input_stocks, "start": input_start, "end": input_end, "threshold": input_threshold, "include_negative": input_negative}
    st.caption("An undirected edge is created when return correlation meets the selected threshold. Default rule: corr ≥ threshold.")

page = st.sidebar.radio("Explore", ["Dashboard & Graph", "Graph Analysis", "Walks & Generating Functions", "Recurrence Lab", "Modular Cycle Analyzer", "Stress Test", "Math Guide"])
config = st.session_state["marketmesh_config"]
selected, start, end, threshold, include_negative = config["stocks"], config["start"], config["end"], config["threshold"], config["include_negative"]
if len(selected) < 2:
    st.warning("Select at least two stocks.")
    st.stop()

upload_fingerprint = hashlib.blake2b(digest_size=16)
for symbol, content in sorted(uploaded_csvs.items()):
    upload_fingerprint.update(symbol.encode("utf-8"))
    upload_fingerprint.update(content)
analysis_signature = (tuple(selected), start.isoformat(), end.isoformat(), float(threshold), bool(include_negative), upload_fingerprint.hexdigest())
try:
    if st.session_state.get("marketmesh_analysis_signature") != analysis_signature:
        prices = manager.align_close_prices(selected, start, end)
        returns = manager.calculate_returns(prices)
        if len(returns) < 2:
            st.warning("Not enough overlapping historical data for this stock selection and date range. Choose a broader period.")
            st.stop()
        correlations = RelationshipAnalyzer.correlation_matrix(returns)
        stock_graph = StockGraph()
        graph = stock_graph.build_graph(selected, correlations, threshold, include_negative)
        st.session_state.update({
            "marketmesh_analysis_signature": analysis_signature,
            "marketmesh_selected_stocks": list(selected),
            "marketmesh_date_range": (start, end),
            "marketmesh_threshold": float(threshold),
            "marketmesh_returns": returns,
            "marketmesh_correlation_matrix": correlations,
            "marketmesh_graph": graph,
            "marketmesh_stock_graph": stock_graph,
            "marketmesh_prices": prices,
        })
    else:
        prices = st.session_state["marketmesh_prices"]
        returns = st.session_state["marketmesh_returns"]
        correlations = st.session_state["marketmesh_correlation_matrix"]
        graph = st.session_state["marketmesh_graph"]
        stock_graph = st.session_state["marketmesh_stock_graph"]
except (ValueError, FileNotFoundError) as exc:
    st.error(str(exc))
    st.stop()


def graph_figure(g, colors=None):
    """Create a lightweight, interactive Plotly rendering of an undirected graph."""
    if not g:
        fig = go.Figure()
        fig.update_layout(height=430, annotations=[dict(text="No vertices to display", showarrow=False, x=0.5, y=0.5, xref="paper", yref="paper")])
        return fig
    pos = nx.spring_layout(g, seed=42)
    edge_traces = []
    for left, right in g.edges:
        x0, y0 = pos[left]
        x1, y1 = pos[right]
        weight = g[left][right].get("weight")
        hover = f"{left} — {right}<br>Return correlation: {weight:.3f}" if weight is not None else f"{left} — {right}"
        edge_traces.append(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", line=dict(width=1 + 2 * abs(weight or 0), color="#94a3b8"), hovertext=[hover, hover], hoverinfo="text", showlegend=False))
    degrees = dict(g.degree())
    component_map = {node: i + 1 for i, component in enumerate(nx.connected_components(g)) for node in component}
    node_trace = go.Scatter(
        x=[pos[n][0] for n in g.nodes], y=[pos[n][1] for n in g.nodes], mode="markers+text",
        text=list(g.nodes), textposition="top center", hovertext=[f"{n}<br>Degree: {degrees[n]}<br>Component: {component_map[n]}" for n in g.nodes], hoverinfo="text",
        marker=dict(size=[16 + 3 * degrees[n] for n in g.nodes], color=[colors.get(n, "#2563eb") if colors else "#2563eb" for n in g.nodes], line=dict(width=1, color="white")),
    )
    fig = go.Figure(edge_traces + [node_trace])
    fig.update_layout(height=490, showlegend=False, margin=dict(l=10, r=10, t=10, b=10), xaxis=dict(visible=False), yaxis=dict(visible=False), plot_bgcolor="white")
    return fig


def render_math_summary(g):
    components = list(nx.connected_components(g))
    cycles = GraphAlgorithms.cycles(g)
    degrees = dict(g.degree())
    highest = max(degrees.values(), default=0)
    euler = GraphAlgorithms.euler_analysis(g)
    columns = st.columns(8)
    columns[0].metric("Vertices", g.number_of_nodes())
    columns[1].metric("Edges", g.number_of_edges())
    columns[2].metric("Components", len(components))
    columns[3].metric("Cycle basis", len(cycles))
    top_nodes = [node for node, degree in degrees.items() if degree == highest] if degrees else []
    columns[4].metric("Highest degree", f"{highest}: {', '.join(top_nodes) if top_nodes else 'none'}")
    columns[5].metric("Euler path", "Yes" if euler["has_path"] else "No")
    columns[6].metric("Euler circuit", "Yes" if euler["has_circuit"] else "No")
    columns[7].metric("Tree", "Yes" if GraphAlgorithms.is_tree(g) else "No")
    st.caption("The highest-degree vertex has the most edges in this selected graph; degree is not a measure of market importance.")
    with st.expander("Euler and tree checks"):
        st.write(f"Odd-degree vertices: {', '.join(euler['odd_vertices']) if euler['odd_vertices'] else 'none'}")
        st.write(f"Euler path: **{'Yes' if euler['has_path'] else 'No'}** · Euler circuit: **{'Yes' if euler['has_circuit'] else 'No'}**")
        st.write(f"Tree: **{'Yes' if GraphAlgorithms.is_tree(g) else 'No'}** (a tree is connected and acyclic)")
    if not g.number_of_edges():
        st.warning("No relationships exceed this threshold. Lower the threshold or choose another period.")


if page == "Dashboard & Graph":
    st.subheader("Historical relationship network")
    st.write(f"Aligned trading dates: {len(prices)} · Return observations: {len(returns)} · Period: {prices.index.min().date()} to {prices.index.max().date()}")
    render_math_summary(graph)
    st.plotly_chart(graph_figure(graph), width="stretch")
    with st.expander("Daily returns and Pearson correlation"):
        st.markdown("Daily return: `Rₜ = (Pₜ − Pₜ₋₁) / Pₜ₋₁`. Correlations compare return changes, never raw price levels.")
        st.dataframe(correlations.style.format("{:.3f}"), width="stretch")
        st.dataframe(returns.tail(10).style.format("{:.4%}"), width="stretch")

elif page == "Graph Analysis":
    st.subheader("Graph Analysis")
    st.plotly_chart(graph_figure(graph), width="stretch")
    degrees = pd.DataFrame(GraphAlgorithms.degrees(graph).items(), columns=["Stock", "Degree"]).sort_values(["Degree", "Stock"], ascending=[False, True])
    left, right = st.columns(2)
    with left:
        st.markdown("#### Vertex degree")
        st.dataframe(degrees, hide_index=True, width="stretch")
        st.markdown("#### Connected components")
        component_rows = [{"Component": i + 1, "Stocks": ", ".join(sorted(nodes)), "Size": len(nodes)} for i, nodes in enumerate(GraphAlgorithms.components(graph))]
        st.dataframe(pd.DataFrame(component_rows), hide_index=True, width="stretch")
    with right:
        st.markdown("#### Graph matrices")
        matrix_tab, weighted_tab, incidence_tab = st.tabs(["Adjacency", "Weighted adjacency", "Incidence"])
        with matrix_tab:
            st.dataframe(stock_graph.get_adjacency_matrix(), width="stretch")
        with weighted_tab:
            st.dataframe(stock_graph.get_adjacency_matrix(weighted=True).style.format("{:.3f}"), width="stretch")
        with incidence_tab:
            st.dataframe(stock_graph.get_incidence_matrix(), width="stretch")
    st.markdown("#### Traversal and path finder")
    source, target = st.columns(2)
    src = source.selectbox("Start / source", selected, key="path_src")
    dst = target.selectbox("Destination", selected, index=min(1, len(selected)-1), key="path_dst")
    bfs_dfs_col, path_col = st.columns(2)
    with bfs_dfs_col:
        traversal = st.selectbox("Traversal", ["BFS", "DFS"])
        order = GraphAlgorithms.bfs(graph, src) if traversal == "BFS" else GraphAlgorithms.dfs(graph, src)
        st.write(f"{traversal} visits the reachable vertices in this order: {' → '.join(order)}")
    with path_col:
        path = GraphAlgorithms.shortest_path(graph, src, dst)
        if path:
            st.write(f"Shortest path ({len(path)-1} edges): {' → '.join(path)}")
        else:
            st.write("No path connects these vertices in the current graph.")
        simple_paths = GraphAlgorithms.simple_paths(graph, src, dst, cutoff=max(1, len(graph)-1), limit=20)
        st.caption(f"Simple paths displayed (limit 20): {len(simple_paths)}")
    st.markdown("#### Cycles and Euler / Hamiltonian properties")
    cycles = GraphAlgorithms.cycles(graph)
    st.write("Detected cycle basis:", [" → ".join(cycle + [cycle[0]]) for cycle in cycles] or "No cycles detected.")
    euler = GraphAlgorithms.euler_analysis(graph)
    st.write(f"Odd-degree vertices: {euler['odd_vertices'] or 'none'}")
    st.write(f"Euler path: {'Yes' if euler['has_path'] else 'No'} · Euler circuit: {'Yes' if euler['has_circuit'] else 'No'}")
    if len(graph) > GraphAlgorithms.HAMILTONIAN_LIMIT:
        st.info("Exact Hamiltonian search is disabled for graphs larger than 12 vertices because exhaustive search becomes expensive.")
    else:
        hpath = GraphAlgorithms.hamiltonian_path(graph)
        hcycle = GraphAlgorithms.hamiltonian_cycle(graph)
        st.write(f"Hamiltonian path: {' → '.join(hpath) if hpath else 'Not found'}")
        st.write(f"Hamiltonian cycle: {' → '.join(hcycle) if hcycle else 'Not found'}")
    st.markdown("#### Stocks-to-sectors bipartite graph")
    sector_graph = nx.Graph()
    sector_graph.add_edges_from((symbol, SECTORS.get(symbol, "Other")) for symbol in selected)
    coloring = GraphAlgorithms.bipartite_coloring(sector_graph)
    st.write("This is bipartite because every edge joins a stock vertex to a sector vertex; no edge joins two stocks or two sectors. That gives a valid two-coloring with no adjacent vertices sharing a color.")
    st.write("Its two color classes are:")
    st.write({"Class 1": sorted(n for n, color in coloring.items() if color == 0), "Class 2": sorted(n for n, color in coloring.items() if color == 1)})

elif page == "Walks & Generating Functions":
    st.subheader("Walk Counting with Adjacency-Matrix Powers")
    st.markdown("For the binary adjacency matrix A, the entry `(Aⁿ)[i,j]` counts length-n walks from i to j. Correlation weights are not used for this count.")
    c1, c2, c3 = st.columns(3)
    walk_source = c1.selectbox("Source stock", selected, key="walk_src")
    walk_target = c2.selectbox("Target stock", selected, index=min(1, len(selected)-1), key="walk_dst")
    max_len = c3.slider("Maximum walk length", 0, 8, 5)
    analyzer = WalkAnalyzer(graph)
    try:
        sequence = analyzer.count_walks(walk_source, walk_target, max_len)
        st.dataframe(pd.DataFrame({"Length n": range(max_len + 1), "Number of walks aₙ": sequence}), hide_index=True, width="stretch")
        polynomial = GeneratingFunctionEngine.polynomial(sequence)
        st.latex(r"G(x) = " + polynomial.replace("*", r"\, "))
        st.caption("The coefficient of xⁿ stores the number of walks of length n between the selected vertices. This is a truncated generating polynomial.")
        with st.expander("Inspect Aⁿ matrices"):
            power_index = st.slider("Show power n", 0, max_len, min(2, max_len))
            st.dataframe(analyzer.power_frames(power_index)[power_index], width="stretch")
    except ValueError as exc:
        st.warning(str(exc))

elif page == "Recurrence Lab":
    st.subheader("Recurrence Relation Laboratory")
    st.write("This module demonstrates how recurrence relations generate discrete sequences that can be compared mathematically with historical patterns. These sequences are not stock forecasts.")
    preset = st.selectbox("Preset", ["Fibonacci", "Second-order homogeneous recurrence", "First-order non-homogeneous recurrence", "Custom supported recurrence"])
    if preset == "Fibonacci":
        c1, c2, constant, a0, a1 = 1, 1, 0, 0, 1
        st.code("a₀ = 0, a₁ = 1; aₙ = aₙ₋₁ + aₙ₋₂")
    else:
        defaults = {
            "Second-order homogeneous recurrence": (2, -1, 0, 1, 2),
            "First-order non-homogeneous recurrence": (2, 0, 3, 1, 0),
            "Custom supported recurrence": (1, 1, 0, 0, 1),
        }
        d1, d2, dd, da0, da1 = defaults[preset]
        controls = st.columns(5)
        c1 = controls[0].number_input("c₁", value=d1, step=1)
        c2 = controls[1].number_input("c₂", value=d2, step=1)
        constant = controls[2].number_input("Constant d", value=dd, step=1)
        a0 = controls[3].number_input("a₀", value=da0, step=1)
        a1 = controls[4].number_input("a₁", value=da1, step=1)
    nterms = st.slider("Number of terms", 2, 40, 12)
    result = RecurrenceSolver.describe(int(c1), int(c2), int(constant), int(a0), int(a1), nterms)
    st.latex(result["equation"])
    st.write(f"Order: {result['order']} · Linear: Yes · Homogeneous: {'Yes' if result['homogeneous'] else 'No'}")
    st.write("Sequence:", result["sequence"])
    st.plotly_chart(go.Figure(go.Scatter(x=list(range(nterms)), y=result["sequence"], mode="lines+markers", name="aₙ")).update_layout(xaxis_title="n", yaxis_title="aₙ", height=350), width="stretch")

elif page == "Modular Cycle Analyzer":
    st.subheader("Modular Arithmetic and CRT Cycle Alignment")
    gcd_tab, inverse_tab, phi_tab, fermat_tab, crt_tab = st.tabs(["GCD / Euclid", "Modular inverse", "Euler phi", "Fermat", "CRT cycle alignment"])
    with gcd_tab:
        a, b = st.columns(2)
        gcd_a = a.number_input("a", value=252, step=1, key="gcd_a")
        gcd_b = b.number_input("b", value=105, step=1, key="gcd_b")
        gcd_value, steps = Modular.gcd(int(gcd_a), int(gcd_b))
        st.write("Euclidean algorithm steps:")
        st.code("\n".join(steps) if steps else "Both inputs are zero.")
        st.success(f"gcd({int(gcd_a)}, {int(gcd_b)}) = {gcd_value}")
        g, x, y = Modular.extended_gcd(int(gcd_a), int(gcd_b))
        st.caption(f"Extended Euclid: {gcd_a}({x}) + {gcd_b}({y}) = {g}")
        divisor = st.number_input("Check whether d divides n", value=3, step=1, key="divisor_d")
        dividend = st.number_input("Integer n", value=252, step=1, key="dividend_n")
        if divisor == 0:
            st.warning("A divisor must be nonzero.")
        else:
            st.write(f"{int(divisor)} {'divides' if Modular.divides(int(divisor), int(dividend)) else 'does not divide'} {int(dividend)}" + (f" (quotient {int(dividend)//int(divisor)})" if Modular.divides(int(divisor), int(dividend)) else f" (remainder {int(dividend)%int(divisor)})"))
    with inverse_tab:
        inverse_a = st.number_input("a", value=7, step=1, key="inv_a")
        inverse_m = st.number_input("Modulus m", value=26, min_value=2, step=1)
        inverse = Modular.modular_inverse(int(inverse_a), int(inverse_m))
        if inverse is None:
            st.warning(f"Inverse does not exist because gcd(a, m) = {Modular.gcd(int(inverse_a), int(inverse_m))[0]}, not 1.")
        else:
            st.success(f"{inverse_a}⁻¹ mod {inverse_m} = {inverse}")
            st.write(f"Verification: {inverse_a} × {inverse} = {int(inverse_a)*inverse} ≡ {(int(inverse_a)*inverse)%int(inverse_m)} (mod {inverse_m})")
    with phi_tab:
        n = st.number_input("Positive integer n", min_value=1, value=9, step=1, key="phi_n")
        factors = Modular.prime_factorization(int(n))
        st.write(f"Prime factorization: {n} = " + (" × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in factors.items()) if factors else "1"))
        st.success(f"φ({n}) = {Modular.phi(int(n))}")
    with fermat_tab:
        fa = st.number_input("a", value=2, step=1, key="fermat_a")
        fp = st.number_input("Prime p", min_value=2, value=7, step=1, key="fermat_p")
        if st.button("Demonstrate Fermat's Little Theorem"):
            try:
                value = Modular.fermat_demo(int(fa), int(fp))
                st.write(f"Since p={fp} is prime and p does not divide a={fa}: a^(p−1) mod p = {value} (expected 1).")
            except ValueError as exc:
                st.error(str(exc))
    with crt_tab:
        st.write("Find the first time several simulated cycles align: x ≡ rᵢ (mod mᵢ). Use pairwise-coprime moduli.")
        residues = [st.number_input(f"Residue r{i+1}", value=r, step=1, key=f"crt_r{i}") for i, r in enumerate([1, 3, 2])]
        moduli = [st.number_input(f"Modulus m{i+1}", min_value=2, value=m, step=1, key=f"crt_m{i}") for i, m in enumerate([4, 5, 7])]
        if st.button("Align cycles with CRT"):
            try:
                solution, modulus, details = Modular.chinese_remainder(list(map(int, residues)), list(map(int, moduli)))
                st.success(f"x ≡ {solution} (mod {modulus}); first nonnegative alignment is {solution}.")
                st.markdown(f"For moduli {list(map(int, moduli))}, the product is `M = {modulus}`. For each row, `Mᵢ = M/mᵢ`, `yᵢ` is the inverse of `Mᵢ modulo mᵢ`, and the row contributes `rᵢMᵢyᵢ`.")
                st.dataframe(pd.DataFrame([{"rᵢ": row["residue"], "mᵢ": row["modulus"], "Mᵢ = M/mᵢ": row["partial"], "yᵢ = Mᵢ⁻¹ mod mᵢ": row["inverse"], "rᵢMᵢyᵢ": row["term"]} for row in details]), hide_index=True, width="stretch")
                st.write(f"`x = Σ(rᵢMᵢyᵢ) mod M = {sum(row['term'] for row in details)} mod {modulus} = {solution}`.")
                st.caption("Each congruence is a simulated repeating event pattern, not a claim that real stock prices are periodic. The combined period is the product of the pairwise-coprime cycle lengths.")
            except ValueError as exc:
                st.error(str(exc))

elif page == "Stress Test":
    st.subheader("Graph Stress Test")
    st.write("Removing a vertex or edge shows how connectivity changes in this selected graph. This describes graph structure, not causality in financial markets.")
    mode = st.radio("Stress operation", ["Remove a vertex", "Remove an edge"], horizontal=True)
    if mode == "Remove a vertex":
        node = st.selectbox("Vertex to remove", list(graph.nodes))
        remaining_nodes = [candidate for candidate in graph.nodes if candidate != node]
        anchor = st.selectbox("Measure reachability from", remaining_nodes) if remaining_nodes else None
        result = GraphStressTester.remove_node(graph, node, anchor)
    elif graph.number_of_edges():
        choices = list(graph.edges)
        edge = st.selectbox("Edge to remove", choices, format_func=lambda pair: f"{pair[0]} — {pair[1]}")
        anchor = st.selectbox("Measure reachability from", list(graph.nodes))
        result = GraphStressTester.remove_edge(graph, *edge, source=anchor)
    else:
        st.info("This graph has no edges to remove.")
        result = None
    if result:
        metrics = ["components", "edges", "largest_component", "reachable_nodes", "cycles"]
        labels = {"components": "Connected components", "edges": "Edges", "largest_component": "Largest component size", "reachable_nodes": "Reachable from selected stock", "cycles": "Cycle basis size"}
        st.dataframe(pd.DataFrame([{ "Metric": labels[key], "Before": result["before"][key], "After": result["after"][key], "Change": result["after"][key] - result["before"][key]} for key in metrics]), hide_index=True, width="stretch")
        before_col, after_col = st.columns(2)
        before_col.markdown("#### Original graph")
        before_col.plotly_chart(graph_figure(graph), width="stretch", key="before_graph")
        after_col.markdown("#### Modified graph")
        after_col.plotly_chart(graph_figure(result["graph"]), width="stretch", key="after_graph")
        st.caption(f"Isolated vertices after removal: {result['after']['isolated_nodes'] or 'none'}")
        st.caption(f"Reachability is measured from {result['before']['source']} before and {result['after']['source']} after removal.")

else:
    st.subheader("Discrete Mathematics Guide")
    st.write("Each feature answers two questions: which mathematical concept is used, and what it means in the current selected stock network.")
    degree_map = dict(graph.degree())
    components = list(nx.connected_components(graph))
    walk_example = WalkAnalyzer(graph).count_walks(selected[0], selected[1], 3)
    example_map = {
        "Daily return and correlation": f"For this selected period, {selected[0]} and {selected[1]} have return correlation {correlations.loc[selected[0], selected[1]]:.3f}; edge status is {'present' if graph.has_edge(selected[0], selected[1]) else 'absent'} at threshold {threshold:.2f}.",
        "Vertex degree": f"{max(degree_map, key=degree_map.get) if degree_map else 'No vertex'} has the highest degree ({max(degree_map.values(), default=0)}).",
        "Connected components": f"This graph has {len(components)} component(s), with sizes {[len(group) for group in components]}.",
        "Adjacency and incidence matrices": f"The displayed binary matrix is {len(graph)}×{len(graph)} and contains {2 * graph.number_of_edges()} ones for {graph.number_of_edges()} undirected edges.",
        "Traversal, paths, and cycles": f"From {selected[0]}, BFS reaches {len(GraphAlgorithms.bfs(graph, selected[0]))} of {len(graph)} vertices; the graph has {len(GraphAlgorithms.cycles(graph))} cycle-basis element(s).",
        "Euler and Hamiltonian properties": f"Current degrees are {degree_map}; Euler analysis reports {len(GraphAlgorithms.euler_analysis(graph)['odd_vertices'])} odd-degree vertices.",
        "Trees and bipartite graphs": f"The selected stock graph is {'a tree' if GraphAlgorithms.is_tree(graph) else 'not a tree'}; the sector graph is two-colorable because every edge crosses stock and sector classes.",
        "Walk counts and adjacency powers": f"From {selected[0]} to {selected[1]}, length 0–3 walk counts are {walk_example}.",
        "Ordinary generating function": f"For that same walk sequence, the truncated polynomial is {GeneratingFunctionEngine.polynomial(walk_example)}.",
        "Recurrence relations": f"Fibonacci starts with a₀=0, a₁=1 and aₙ=aₙ₋₁+aₙ₋₂; its first six terms are {RecurrenceSolver.fibonacci(6)}.",
        "Divisibility and Euclidean algorithms": f"For the displayed GCD inputs {int(st.session_state.get('gcd_a', 252))} and {int(st.session_state.get('gcd_b', 105))}, gcd is {Modular.gcd(int(st.session_state.get('gcd_a', 252)), int(st.session_state.get('gcd_b', 105)))[0]}; 3 divides 252.",
        "Modular inverse and congruences": f"For example, 7×15≡1 (mod 26), so 15 is the inverse of 7 modulo 26; 4x≡2 (mod 6) has residues {Modular.solve_congruence(4, 2, 6)}.",
        "Primes, Euler phi, and Fermat": f"For n=9, φ(9)={Modular.phi(9)}; since 7 is prime, 2⁶≡{Modular.fermat_demo(2, 7)} (mod 7).",
        "Chinese Remainder Theorem": f"The example x≡1 (mod 4), x≡3 (mod 5), x≡2 (mod 7) gives x≡{Modular.chinese_remainder([1, 3, 2], [4, 5, 7])[0]} (mod 140).",
        "Graph stress test": f"Removing an edge or vertex from this graph recomputes component, reachability, and cycle metrics for comparison.",
    }
    for concept, details in CONCEPTS.items():
        with st.expander(concept):
            st.markdown(f"**Definition:** {details['definition']}")
            st.markdown(f"**How MarketMesh uses it:** {details['use']}")
            st.markdown(f"**Formula / algorithm:** {details['method']}")
            st.markdown(f"**Current example:** {example_map[concept]}")
    st.markdown("#### Syllabus coverage")
    st.markdown("- **Unit 4:** recurrence relations, Fibonacci sequence, graph walk counts, truncated ordinary generating polynomials.\n- **Unit 5:** divisibility, Euclidean and extended Euclidean algorithms, modular inverse, primes, factorization, Euler phi, Fermat’s Little Theorem, congruences, CRT.\n- **Unit 6:** graph representations, degree, components, BFS/DFS, paths, cycles, Euler/Hamiltonian properties, trees, bipartite graphs, stress testing.")

with st.sidebar:
    st.divider()
    st.caption("MarketMesh is an educational discrete mathematics project. No forecasts, recommendations, or trading integrations are provided.")
