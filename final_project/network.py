"""
network.py

The Project class lives here.
"""

from contextlib import contextmanager

import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import osmnx as ox
import networkx as nx
import numpy as np
from networkx.readwrite import write_gpickle, read_gpickle

from .cartography import NetworkMapper
from .routing import RoutingMixin
from .utilities import nearest_k_nodes
from .merge import convert_length_to_meter


class Network(RoutingMixin):

    mapper = NetworkMapper()

    def __init__(self, G: nx.Graph):
        self.G = G

    def __getitem__(self, node_id):
        """Returns the Graph node adjacency view by subscripting"""
        return self.G[node_id]

    @property
    def nodes(self):
        return self.G.nodes

    @property
    def edges(self):
        return self.G.edges

    @property
    def nodes_df(self):
        node_list = [
            {"id": node[0], "y": node[1]["y"], "x": node[1]["x"]}
            for node in list(self.G.nodes(data=True))
        ]
        return pd.DataFrame(node_list)

    @property
    def edges_df(self):
        return nx.to_pandas_edgelist(self.G)

    @property
    def edges_with_nodes_df(self):
        nodes_df = self.nodes_df
        edges_df = self.edges_df
        edges_df = edges_df.merge(nodes_df, left_on="source", right_on="id", how="left")
        edges_df = edges_df.merge(
            nodes_df,
            left_on="target",
            right_on="id",
            how="left",
            suffixes=("_source", "_target"),
        )
        return edges_df

    @property
    def extent_polygon(self):
        """Returns the geographic extent of the network via the convex hull method

        Code attribution: http://kuanbutts.com/2018/12/24/peartree-with-walk-network/"""
        boundary = gpd.GeoSeries(
            [Point(n["x"], n["y"]) for i, n in self.G.nodes(data=True)]
        ).unary_union.convex_hull
        return boundary

    @property
    def bounding_box(self):
        """returns the Upper Left and lower right bounding box of the Network bounds
        """
        (minx, miny, maxx, maxy) = self.extent_polygon.bounds
        return [(maxy, maxx), (miny, minx)]

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

    @classmethod
    def load(cls, filepath):
        raise NotImplementedError


class TransitNetwork(Network):

    mapper = NetworkMapper(
        color_by_col="mode", color_scheme={"transit": "blue"}, popup_info=["length"]
    )

    def __init__(self, graph):
        super().__init__(graph)
        # TODO Enforce schema

    @classmethod
    def load(cls, filepath):
        graph = read_gpickle(filepath)
        return cls(graph)


class WalkNetwork(Network):

    mapper = NetworkMapper(
        color_by_col=None, color_scheme=None, popup_info=["osmid", "name", "length"]
    )

    def __init__(self, graph):
        super().__init__(graph)
        # TODO Enforce schema

    @classmethod
    def load(cls, filepath):
        graph = ox.io.load_graphml(filepath)
        return cls(graph)

    def save(self):  # To file
        raise NotImplementedError


class MultiNetwork(TransitNetwork):
    mapper = NetworkMapper(
        color_by_col="mode",
        color_scheme={"transit": "blue", "walk": "darkgrey"},
        popup_info=["mode", "osmid", "length"],
    )

    def __init__(self, graph):
        super().__init__(graph)

    @classmethod
    def combine(cls, walk: WalkNetwork, transit: TransitNetwork):

        walk.G = convert_length_to_meter(walk.G)

        transit_nodes = ox.utils_graph.graph_to_gdfs(
            transit.G, edges=False, node_geometry=True
        )

        xarr = transit_nodes["x"].to_numpy()
        yarr = transit_nodes["y"].to_numpy()

        nodes, dist = nearest_k_nodes(walk.G, X=xarr, Y=yarr, k=1, return_dist=True)
        nodes_flat = np.array(nodes).reshape(len(nodes))
        dist_flat = np.array(dist).reshape(len(dist))

        transit_nodes = (
            transit_nodes.reset_index()
            .join(pd.Series(nodes_flat, name="nearest_node"))
            .join(pd.Series(dist_flat, name="dist"))
        )

        def convert_meters_to_seconds(m, kph=4.5):
            kilometers = m / 1000
            hours = kilometers / kph
            return hours * 60 * 60

        transit_nodes["time"] = transit_nodes["dist"].apply(convert_meters_to_seconds)

        G = nx.union(walk.G, transit.G)

        transit_tuples = [
            (row[0], row[6], dict(length=row[8], mode="walk"))
            for _, row in transit_nodes.iterrows()
        ]
        G.add_edges_from(transit_tuples)
        transit_tuples_reverse = [
            (row[6], row[0], dict(length=row[8], mode="walk"))
            for _, row in transit_nodes.iterrows()
        ]
        G.add_edges_from(transit_tuples_reverse)
        return cls(graph=G)
