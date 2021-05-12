"""cartography.py

NetworkMapper lives here - the helper Descriptor for the Network class.
"""
import folium
from typing import List


class NetworkMapper:
    """
    To be used as a descriptor with the network.Network class and subclasses.
    Works with the Network's nodes and edges.

    Example:
        n = Network()
        n.mapper  # returns Folium map

    """

    DEFAULT_NODE_COLOR = "black"

    def __init__(
        self,
        color_by_col: str = None,
        color_scheme: dict = None,
        popup_info: List[str] = None,
    ):
        """

        Args:
            color_by_col (str): Network attribute to color the map by
            color_scheme (dict): how to color the map. ex: {"transit": "blue"}
            popup_info (List[str]): What to display on the map popup
        """
        self.m = folium.Map()
        self.color_by_col = color_by_col
        self.color_scheme = color_scheme
        self.popup_info = popup_info

    def __get__(self, obj, nodes=True, edges=True):
        """Helper method that facilitates the n.mapper call"""
        if nodes:
            self._add_nodes(graph=obj)
        if edges:
            self._add_edges(graph=obj)

        self.m.fit_bounds(bounds=obj.bounding_box)
        return self.m

    def _add_nodes(self, graph):
        """Private method to map nodes.

        Args:
            graph (Network): network whose nodes to map. gets passed in via __get__()

        Returns:
            Nothing, adds nodes to the Folium map, self.m
        """
        node_list = [
            [graph.nodes.get(node)["y"], graph.nodes.get(node)["x"]]
            for node in graph.nodes
        ]
        node_info_list = [
            {"node_id": node, "neighbors": list(graph[node])} for node in graph.nodes
        ]

        for i, (node, info) in enumerate(zip(node_list, node_info_list)):
            folium.Marker(node, popup=info).add_to(self.m)

    def _add_edges(self, graph):
        """Private method to map edges.

        Args:
            graph (Network): network whose edges to map. gets passed in via __get__()

        Returns:
            Nothing, adds edges to the Folium map, self.m
        """
        edges_df = graph.edges_with_nodes_df

        if self.color_by_col:
            edges_df["color"] = edges_df[self.color_by_col].replace(self.color_scheme)
        else:
            edges_df["color"] = self.DEFAULT_NODE_COLOR

        source_list = edges_df[["y_source", "x_source"]].values.tolist()
        target_list = edges_df[["y_target", "x_target"]].values.tolist()
        popup_list = edges_df[self.popup_info].values.tolist()
        color_list = edges_df[["color"]].values.tolist()

        for i, (source, target, popup, color) in enumerate(
            zip(source_list, target_list, popup_list, color_list)
        ):
            folium.PolyLine(
                locations=[source, target], popup=popup, color=color
            ).add_to(self.m)
