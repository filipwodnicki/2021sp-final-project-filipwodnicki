import folium
from typing import List


class NetworkMapper:
    DEFAULT_NODE_COLOR = "black"

    def __init__(
        self,
        color_by_col: dict = None,
        color_scheme: dict = None,
        popup_info: List[str] = None,
    ):
        self.m = folium.Map()
        self.color_by_col = color_by_col
        self.color_scheme = color_scheme
        self.popup_info = popup_info

    def __get__(self, obj, nodes=True, edges=True):
        if nodes:
            self._add_nodes(graph=obj)
        if edges:
            self._add_edges(graph=obj)

        self.m.fit_bounds(bounds=obj.bounding_box)
        return self.m

    def _add_nodes(self, graph):
        # Add nodes
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
