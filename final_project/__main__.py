import peartree as pt
import networkx
import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point
from networkx.readwrite import write_gpickle, read_gpickle

from .utilities import nearest_k_nodes
from .viz import create_polygon_map, create_fancy_graph_map
from . import merge


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


def load_osmnx_graph(filepath):
    graph = ox.io.load_graphml(filepath)
    return graph


def load_peartree_graph(filepath):
    graph = read_gpickle(filepath)
    return graph


def make_nodes_df_from_pg(peartree_graph):
    return ox.utils_graph.graph_to_gdfs(peartree_graph, edges=False, node_geometry=True)


if __name__ == "__main__":
    OG = load_osmnx_graph(filepath=NOLA_WALKING_PICKLE)
    PG = load_peartree_graph(filepath=NOLA_TRANSIT_PICKLE)

    pg_nodes = make_nodes_df_from_pg(PG)

    xarr = pg_nodes["x"].to_numpy()
    yarr = pg_nodes["y"].to_numpy()

    nodes, dist = nearest_k_nodes(OG, X=xarr[0:10], Y=yarr[0:10], k=1, return_dist=True)
    print("nodes", nodes)
    print("dist", dist)

    print("stop")
