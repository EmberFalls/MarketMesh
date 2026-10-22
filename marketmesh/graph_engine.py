"""Construct and represent the undirected stock relationship graph."""

import networkx as nx
import pandas as pd


class StockGraph:
    def __init__(self) -> None:
        self.graph = nx.Graph()

    def build_graph(self, symbols, correlation_matrix: pd.DataFrame, threshold: float, include_negative=False):
        if not -1 <= threshold <= 1:
            raise ValueError("Correlation threshold must be between -1 and 1.")
        self.graph = nx.Graph()
        self.graph.add_nodes_from(symbols)
        symbols = list(symbols)
        for i, left in enumerate(symbols):
            for right in symbols[i + 1 :]:
                weight = correlation_matrix.loc[left, right]
                if pd.notna(weight) and (abs(weight) >= threshold if include_negative else weight >= threshold):
                    self.graph.add_edge(left, right, weight=float(weight))
        return self.graph

    def get_graph(self):
        return self.graph

    def get_vertices(self):
        return list(self.graph.nodes)

    def get_edges(self):
        return list(self.graph.edges(data=True))

    def get_adjacency_matrix(self, weighted=False) -> pd.DataFrame:
        return nx.to_pandas_adjacency(self.graph, nodelist=list(self.graph.nodes), weight="weight" if weighted else None, dtype=float if weighted else int)

    def get_incidence_matrix(self) -> pd.DataFrame:
        vertices = list(self.graph.nodes)
        edges = list(self.graph.edges)
        matrix = [[int(vertex in edge) for edge in edges] for vertex in vertices]
        labels = [f"e{i + 1}: {left}-{right}" for i, (left, right) in enumerate(edges)]
        return pd.DataFrame(matrix, index=vertices, columns=labels)

    def num_vertices(self) -> int:
        return self.graph.number_of_nodes()

    def num_edges(self) -> int:
        return self.graph.number_of_edges()
