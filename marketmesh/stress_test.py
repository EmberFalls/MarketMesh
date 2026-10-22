"""Compare graph connectivity before and after node or edge removal."""

import networkx as nx


class GraphStressTester:
    @staticmethod
    def metrics(graph, source=None):
        components = list(nx.connected_components(graph))
        largest = max(components, key=len, default=set())
        if source not in graph:
            source = next(iter(largest), None)
        reachable = nx.node_connected_component(graph, source) if source is not None else set()
        return {
            "components": len(components),
            "edges": graph.number_of_edges(),
            "largest_component": len(largest),
            "reachable_nodes": len(reachable),
            "source": source,
            "cycles": len(nx.cycle_basis(graph)),
            "isolated_nodes": list(nx.isolates(graph)),
        }

    @classmethod
    def remove_node(cls, graph, node, source=None):
        before = cls.metrics(graph, source)
        modified = graph.copy()
        modified.remove_node(node)
        after_source = source if source in modified else None
        return {"graph": modified, "before": before, "after": cls.metrics(modified, after_source)}

    @classmethod
    def remove_edge(cls, graph, left, right, source=None):
        before = cls.metrics(graph, source)
        modified = graph.copy()
        modified.remove_edge(left, right)
        return {"graph": modified, "before": before, "after": cls.metrics(modified, source)}
