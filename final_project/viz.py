import folium
import osmnx as ox
import networkx
import webbrowser
import pathlib


def create_polygon_map(polygon, outfile):
    (y, x) = polygon.centroid.y, polygon.centroid.x
    m = folium.Map(location=[y, x])
    folium.GeoJson(polygon).add_to(m)
    m.save(outfile)
    open_map_browser(outfile)


def create_graph_map(graph, outfile, **plotting_kwargs):
    first_node = list(graph.nodes())[0]
    y, x = graph.nodes.get(first_node)["y"], graph.nodes.get(first_node)["x"]
    m = folium.Map(location=[y, x])
    m = ox.folium.plot_graph_folium(graph, graph_map=m, fit_bounds=True)
    m.save(outfile)
    open_map_browser(outfile)


def create_fancy_graph_map(graph, outfile, edge_attr, color_scheme):
    first_node = list(graph.nodes())[0]
    y, x = graph.nodes.get(first_node)["y"], graph.nodes.get(first_node)["x"]
    m = folium.Map(location=[y, x])
    graph_df = networkx.convert_matrix.to_pandas_edgelist(graph)
    for mode, color in color_scheme.items():
        subgraph_df = graph_df[graph_df[edge_attr] == mode]
        subgraph_nodes = subgraph_df["source"].tolist() + subgraph_df["target"].tolist()
        subgraph = graph.subgraph(subgraph_nodes)
        if len(list(subgraph.edges)) > 0:
            m = ox.folium.plot_graph_folium(
                subgraph, graph_map=m, color=color, edge_attribute=edge_attr
            )
    m.save(outfile)
    open_map_browser(outfile)
    return m


def open_map_browser(outfile):
    c = webbrowser.get("chrome")
    m_uri = pathlib.Path(outfile).absolute().as_uri()
    c.open_new_tab(m_uri)
