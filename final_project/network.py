"""
network.py

The Project class lives here.
"""

from contextlib import contextmanager
import networkx as nx


class Network:
    def __init__(self, G: nx.Graph):
        self.G = G

    @property  # Advanced Python
    def nodes(self):
        return self.G.nodes

    @property
    def edges(self):
        return self.G.edges

    @contextmanager
    def open_as_edges_df(self, nx_graph_constructor=nx.MultiDiGraph):
        try:
            df = nx.convert_matrix.to_pandas_edgelist(self.G)
            yield df
        finally:
            print(f"Overwriting {self.G}")
            self.G = nx.convert_matrix.from_pandas_edgelist(
                df, edge_attr=True, create_using=nx_graph_constructor
            )

    def _do_something_on_nodes(self, function):
        pass

    def _get_node_nearest_point(self, point):
        pass

    def get_shortest_route(self, A, B, k=1):
        """

        :param A:
        :type A:
        :param B:
        :type B:
        :param k: number of nearest nodes to each A and B to consider
        :type k:
        :return:
        :rtype:
        """
        pass


class CombinedNetwork(Network):
    def __init__(self, G1, G2):
        # Run checks to combine networks
        pass
