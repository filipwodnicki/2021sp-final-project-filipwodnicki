import peartree as pt
import networkx
import osmnx as ox
from networkx.readwrite import write_gpickle, read_gpickle


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


# We need a coverage area, based on the points from the
# New Orleans GTFS data, which we can pull from the peartree
# network graph by utilizing coordinate values and extracting
# a convex hull from the point cloud


def main():
    print("Loading Peartree feed")
    # PG = peartree_helper(NOLA_TRANSIT_PICKLE)
    # n = Network(PG)
    # write_gpickle(PG, "data/nola_transit_network.pickle")

    # print(n.nodes[:10])


def load_osmnx_graph(filepath):
    graph = ox.io.load_graphml(filepath)
    return graph


def load_peartree_graph(filepath):
    graph = read_gpickle(filepath)
    return graph


def make_nodes_df_from_pg(peartree_graph):
    return ox.utils_graph.graph_to_gdfs(peartree_graph, edges=False, node_geometry=True)


if __name__ == "__main__":
    main()
