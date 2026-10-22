import networkx as nx

from marketmesh.graph_algorithms import GraphAlgorithms as Algorithms


def test_graph_properties_and_traversal():
    graph = nx.cycle_graph(["A", "B", "C", "D"])
    assert graph.number_of_nodes() == 4
    assert graph.number_of_edges() == 4
    assert dict(graph.degree())["A"] == 2
    assert len(Algorithms.components(graph)) == 1
    assert Algorithms.bfs(graph, "A")[0] == "A"
    assert Algorithms.dfs(graph, "A")[0] == "A"
    assert Algorithms.cycles(graph)
    assert Algorithms.euler_analysis(graph)["has_circuit"]
    assert Algorithms.is_tree(graph) is False


def test_paths_and_euler_path():
    graph = nx.path_graph(["A", "B", "C"])
    assert Algorithms.shortest_path(graph, "A", "C") == ["A", "B", "C"]
    result = Algorithms.euler_analysis(graph)
    assert result["has_path"] is True
    assert result["has_circuit"] is False


def test_hamiltonian_path_cycle_and_disconnection():
    triangle = nx.cycle_graph(["A", "B", "C"])
    assert Algorithms.hamiltonian_path(triangle)
    assert Algorithms.hamiltonian_cycle(triangle)
    disconnected = nx.Graph([("A", "B"), ("C", "D")])
    assert Algorithms.hamiltonian_path(disconnected) is None


def test_bipartite_and_hamiltonian_size_guard():
    bipartite = nx.Graph([("TCS", "IT"), ("INFY", "IT"), ("HDFC", "Banking")])
    assert Algorithms.bipartite_coloring(bipartite) is not None
    assert Algorithms.bipartite_coloring(nx.cycle_graph(3)) is None
    large = nx.complete_graph(Algorithms.HAMILTONIAN_LIMIT + 1)
    try:
        Algorithms.hamiltonian_path(large)
    except ValueError:
        pass
    else:
        raise AssertionError("Hamiltonian search should enforce its size limit")
