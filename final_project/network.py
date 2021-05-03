"""
network.py

The Project class lives here.
"""

import networkx as nx


class Network:
    nodes = None  # descriptor
    edges = None  # descriptor

    def __init__(self, G: nx.Graph):
        self.G = G
        # run checks on the network

    def nodes_descriptor(self):
        pass

    def edges_descriptor(self):
        pass

    def _do_something_on_nodes(self, function):
        pass

    def _do_something_on_edges(self, function):
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
