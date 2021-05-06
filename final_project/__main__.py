from network import Network
import pathlib
import peartree as pt
import networkx
from networkx.readwrite import write_gpickle, read_gpickle
import osmnx as ox
import webbrowser
import folium
from .utilities import nearest_k_nodes

NOLA_GTFS_ZIP = "data/nola_gtfs.zip"
NOLA_TRANSIT_PICKLE = "data/nola_transit_network.pickle"
NOLA_MAP = "data/nola_map.html"
NOLA_WALKING_PICKLE = "data/nola_walking_network.graphml"
NOLA_WALKING_MAP = "data/nola_walking_map.html"
COMBINED_GRAPH_PICKLE = "data/nola_combined_network.pickle"


def peartree_helper(gtfs_feed_zip) -> networkx.Graph:
    feed = pt.get_representative_feed(gtfs_feed_zip)
    start = 7 * 60 * 60
    end = 9 * 60 * 60
    G = pt.load_feed_as_graph(feed, start, end)
    return G


import geopandas as gpd
from shapely.geometry import Point

# We need a coverage area, based on the points from the
# New Orleans GTFS data, which we can pull from the peartree
# network graph by utilizing coordinate values and extracting
# a convex hull from the point cloud


def get_boundary_of_graph(G):
    """
    Function attributable to code in:
    http://kuanbutts.com/2018/12/24/peartree-with-walk-network/

    :param G: Graph network
    :return: Shapely Polygon 
    """
    boundary = gpd.GeoSeries(
        [Point(n["x"], n["y"]) for i, n in G.nodes(data=True)]
    ).unary_union.convex_hull
    return boundary


def main():
    print("Loading Peartree feed")
    # PG = peartree_helper(NOLA_TRANSIT_PICKLE)
    # n = Network(PG)
    # write_gpickle(PG, "data/nola_transit_network.pickle")

    # print(n.nodes[:10])


def create_polygon_map(polygon, outfile):
    (y, x) = polygon.centroid.y, polygon.centroid.x
    m = folium.Map(location=[y, x])
    folium.GeoJson(boundary).add_to(m)
    m.save(outfile)
    open_map_browser(outfile)


def create_graph_map(graph, outfile, **plotting_kwargs):
    first_node = list(graph.nodes())[0]
    y, x = graph.nodes.get(first_node)["y"], graph.nodes.get(first_node)["x"]
    m = folium.Map(location=[y, x])
    m = ox.folium.plot_graph_folium(graph, graph_map=m, fit_bounds=True)
    m.save(outfile)
    open_map_browser(outfile)


def open_map_browser(outfile):
    c = webbrowser.get("chrome")
    m_uri = pathlib.Path(outfile).absolute().as_uri()
    c.open_new_tab(m_uri)


def convert_length_to_meter(osmnx_graph):
    """
    from http://kuanbutts.com/2018/12/24/peartree-with-walk-network/

    :param osmnx_graph:
    :type osmnx_graph:
    :return:
    :rtype:
    """
    walk_speed = 4.5  # about 3 miles per hour

    # Make a copy of the graph in case we make a mistake
    Gwalk_adj = osmnx_graph.copy()

    # Iterate through and convert lengths to seconds
    for from_node, to_node, edge in Gwalk_adj.edges(data=True):
        orig_len = edge["length"]

        # Note that this is a MultiDiGraph so there could
        # be multiple indices here, I naively assume this is not
        # the case
        Gwalk_adj[from_node][to_node][0]["orig_length"] = orig_len

        # Conversion of walk speed and into seconds from meters
        kmph = (orig_len / 1000) / walk_speed
        in_seconds = kmph * 60 * 60
        Gwalk_adj[from_node][to_node][0]["length"] = in_seconds

        # And state the mode, too
        Gwalk_adj[from_node][to_node][0]["mode"] = "walk"

    # So this should be easy - just go through all nodes
    # and make them have a 0 cost to board
    for i, node in Gwalk_adj.nodes(data=True):
        Gwalk_adj.nodes.get(i)["boarding_cost"] = 0

    return Gwalk_adj


def cleanup_graph(peartree_graph):
    """http://kuanbutts.com/2018/12/24/peartree-with-walk-network/"""

    # This is an issue that needs cleaning up
    # slash I need to look into it more
    # but some nodes that should have been
    # cleaned out remain
    print("All nodes", len(peartree_graph.nodes()))
    bad_ns = [i for i, n in peartree_graph.nodes(data=True) if "x" not in n]
    print("Bad nodes count", len(bad_ns))

    for bad_n in bad_ns:
        # Make sure they do not conenct to anything
        if len(peartree_graph[bad_n]) > 0:
            # This should not happen
            print(bad_n)

        else:
            # So just drop them
            peartree_graph.remove_node(bad_n)

    return peartree_graph


def combine(NOLA_WALKING_PICKLE, NOLA_GTFS_ZIP):
    # Gwalk = ox.graph_from_polygon(boundary, network_type="walk")
    # ox.plot_graph(Gwalk)
    # ox.io.save_graphml(Gwalk, filepath=NOLA_WALKING_PICKLE, encoding="utf-8")
    Gwalk = ox.io.load_graphml(filepath=NOLA_WALKING_PICKLE)
    # create_graph_map(Gwalk, NOLA_WALKING_MAP)

    # ------- COMBINE BLOCK -------
    print("Combining the graphs")
    Gwalk_adj = convert_length_to_meter(Gwalk)
    feed = pt.get_representative_feed(NOLA_GTFS_ZIP)
    # Now that we have a formatted walk network
    # it should be easy to reload the peartree graph
    # and stack it on the walk network
    start = 7 * 60 * 60
    end = 9 * 60 * 60
    # Note this will be a little slow - an optimization here would be
    # to have coalesced the walk network
    G2 = pt.load_feed_as_graph(feed, start, end, existing_graph=Gwalk_adj)
    G = cleanup_graph(G2)
    # ----- END COMBINE BLOCK -----

    write_gpickle(G, COMBINED_GRAPH_PICKLE)


if __name__ == "__main__":
    # main()
    # PG = read_gpickle(NOLA_TRANSIT_PICKLE)

    print("Getting the walking graph")
    # combine(NOLA_WALKING_PICKLE, NOLA_GTFS_ZIP)
    G = read_gpickle(COMBINED_GRAPH_PICKLE)

    print("Making a map")
    boundary = get_boundary_of_graph(G)
    create_polygon_map(polygon=boundary, outfile=NOLA_MAP)

    pt1 = (29.922279216104823, -90.11460261754031)
    pt2 = (29.921460143478885, -90.09538679522964)
    print("stop")
