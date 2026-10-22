import networkx as nx
import pandas as pd

from marketmesh.graph_engine import StockGraph
from marketmesh.relationship import RelationshipAnalyzer
from marketmesh.stress_test import GraphStressTester


def test_correlation_edges_and_threshold_validation():
    returns = pd.DataFrame({"A": [1, 2, 3, 4], "B": [2, 4, 6, 8], "C": [4, 3, 2, 1]})
    correlations = RelationshipAnalyzer.correlation_matrix(returns)
    graph = StockGraph().build_graph(returns.columns, correlations, 0.8)
    assert graph.has_edge("A", "B")
    assert not graph.has_edge("A", "C")
    negative_graph = StockGraph().build_graph(returns.columns, correlations, 0.8, include_negative=True)
    assert negative_graph.has_edge("A", "C")
    try:
        RelationshipAnalyzer.qualifying_pairs(correlations, 1.1)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid thresholds should be rejected")


def test_incidence_matrix_is_labeled_and_binary():
    correlations = pd.DataFrame([[1, 0.9, 0.1], [0.9, 1, 0.8], [0.1, 0.8, 1]], index=["A", "B", "C"], columns=["A", "B", "C"])
    wrapper = StockGraph()
    wrapper.build_graph(["A", "B", "C"], correlations, 0.7)
    incidence = wrapper.get_incidence_matrix()
    assert incidence.shape == (3, 2)
    assert all(value in (0, 1) for value in incidence.to_numpy().ravel())
    assert all(str(column).startswith("e") for column in incidence.columns)


def test_stress_metrics_track_reachability_and_cycles():
    graph = nx.Graph([("A", "B"), ("B", "C"), ("C", "A"), ("C", "D")])
    result = GraphStressTester.remove_node(graph, "C", source="A")
    assert result["before"]["reachable_nodes"] == 4
    assert result["after"]["reachable_nodes"] == 2
    assert result["before"]["cycles"] == 1
    assert result["after"]["cycles"] == 0
