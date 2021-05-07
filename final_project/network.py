"""
network.py

The Project class lives here.
"""

from contextlib import contextmanager
import networkx as nx
from cartography import CartographyMixin
from routing import RoutingMixin


class Network(CartographyMixin, RoutingMixin):

    # parameter... what is that thing called?

    def __init__(self, G: nx.Graph):
        self.G = G

    @property  # Advanced Python
    def nodes(self):
        return self.G.nodes

    @property
    def edges(self):
        return self.G.edges

    @property
    def extent(self):
        # TODO Polygon geographic extent
        raise NotImplementedError

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

    def _add_nodes(self):
        pass


class TransitNetwork(Network):
    def __init__(self, gtfs_zip):
        self.G = ""  # initialize from GTFS via peartree


class WalkNetwork(Network):
    def __init__(self):
        # Enforce a schema, where nodes have type walking and length seconds
        pass  # double constructor. From graphml file, and from polygon

    def save(self):  # To file
        raise NotImplementedError


class MultiNetwork(Network):
    def __init__(self, G1, G2):
        # Run checks to combine networks
        # _add_nodes()
        raise NotImplementedError
