"""Educational graph algorithms with small-graph Hamiltonian search."""

from collections import deque
import networkx as nx


class GraphAlgorithms:
    HAMILTONIAN_LIMIT = 12

    @staticmethod
    def degrees(graph):
        return dict(graph.degree())

    @staticmethod
    def components(graph):
        return [set(component) for component in nx.connected_components(graph)]

    @staticmethod
    def bfs(graph, start):
        if start not in graph:
            return []
        seen, queue, order = {start}, deque([start]), []
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in sorted(graph.neighbors(node), key=str):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        return order

    @staticmethod
    def dfs(graph, start):
        if start not in graph:
            return []
        seen, stack, order = set(), [start], []
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            order.append(node)
            stack.extend(sorted((n for n in graph.neighbors(node) if n not in seen), key=str, reverse=True))
        return order

    @staticmethod
    def shortest_path(graph, source, target):
        try:
            return nx.shortest_path(graph, source, target)
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return None

    @staticmethod
    def simple_paths(graph, source, target, cutoff=None, limit=20):
        if source not in graph or target not in graph:
            return []
        return list(__import__("itertools").islice(nx.all_simple_paths(graph, source, target, cutoff=cutoff or max(0, len(graph) - 1)), limit))

    @staticmethod
    def cycles(graph):
        return nx.cycle_basis(graph)

    @staticmethod
    def euler_analysis(graph):
        odd = [node for node, degree in graph.degree() if degree % 2]
        nonisolated = [node for node, degree in graph.degree() if degree]
        connected = not nonisolated or nx.is_connected(graph.subgraph(nonisolated))
        path = connected and len(odd) in (0, 2)
        circuit = connected and len(odd) == 0
        return {"odd_vertices": odd, "connected_nonisolated": connected, "has_path": path, "has_circuit": circuit}

    @classmethod
    def hamiltonian_path(cls, graph):
        if len(graph) > cls.HAMILTONIAN_LIMIT:
            raise ValueError(f"Exact Hamiltonian search is limited to {cls.HAMILTONIAN_LIMIT} vertices.")
        if not graph:
            return []
        def search(node, path, used):
            if len(path) == len(graph):
                return list(path)
            for neighbor in graph.neighbors(node):
                if neighbor not in used:
                    result = search(neighbor, path + [neighbor], used | {neighbor})
                    if result:
                        return result
            return None
        for start in graph.nodes:
            result = search(start, [start], {start})
            if result:
                return result
        return None

    @classmethod
    def hamiltonian_cycle(cls, graph):
        if len(graph) > cls.HAMILTONIAN_LIMIT:
            raise ValueError(f"Exact Hamiltonian search is limited to {cls.HAMILTONIAN_LIMIT} vertices.")
        if not graph:
            return None
        start = next(iter(graph.nodes))
        def search(node, path, used):
            if len(path) == len(graph):
                return path + [start] if graph.has_edge(node, start) else None
            for neighbor in graph.neighbors(node):
                if neighbor not in used:
                    result = search(neighbor, path + [neighbor], used | {neighbor})
                    if result:
                        return result
            return None
        return search(start, [start], {start})

    @staticmethod
    def is_tree(graph):
        return nx.is_tree(graph) if graph else False

    @staticmethod
    def bipartite_coloring(graph):
        if not nx.is_bipartite(graph):
            return None
        return nx.bipartite.color(graph)
