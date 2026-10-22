"""Count graph walks using powers of the binary adjacency matrix."""

import numpy as np
import pandas as pd


class WalkAnalyzer:
    def __init__(self, graph) -> None:
        self.nodes = list(graph.nodes)
        self.index = {node: i for i, node in enumerate(self.nodes)}
        self.adjacency = nx_to_binary(graph, self.nodes)

    def powers(self, max_length: int):
        if max_length < 0 or max_length > 8:
            raise ValueError("Maximum walk length must be between 0 and 8.")
        powers = [np.eye(len(self.nodes), dtype=object)]
        for _ in range(max_length):
            powers.append(powers[-1] @ self.adjacency)
        return powers

    def count_walks(self, source, target, max_length: int):
        if source not in self.index or target not in self.index:
            raise ValueError("Source and target must be graph vertices.")
        i, j = self.index[source], self.index[target]
        powers = self.powers(max_length)
        return [int(power[i, j]) for power in powers]

    def power_frames(self, max_length: int):
        return [pd.DataFrame(power, index=self.nodes, columns=self.nodes) for power in self.powers(max_length)]


def nx_to_binary(graph, nodes):
    return np.array([[int(graph.has_edge(a, b)) for b in nodes] for a in nodes], dtype=object)
