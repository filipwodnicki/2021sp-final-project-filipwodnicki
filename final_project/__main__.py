import peartree as pt
import networkx
import geopandas as gpd
from shapely.geometry import Point
from networkx.readwrite import write_gpickle, read_gpickle

from utilities import nearest_k_nodes
from viz import create_polygon_map, create_fancy_graph_map
import merge

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


if __name__ == "__main__":
    # main()
    # PG = read_gpickle(NOLA_TRANSIT_PICKLE)

    print("Getting the walking graph")
    merge.combine(NOLA_WALKING_PICKLE, NOLA_GTFS_ZIP, COMBINED_GRAPH_PICKLE)
    # G = read_gpickle(COMBINED_GRAPH_PICKLE)

    # print("Making a map")
    # boundary = get_boundary_of_graph(G)
    # create_polygon_map(polygon=boundary, outfile=NOLA_MAP)

    pt1 = (29.922279216104823, -90.11460261754031)
    pt2 = (29.921460143478885, -90.09538679522964)

    # print("Making a fancy map")
    # nodes = nearest_k_nodes(G, pt1[1], pt1[0], k=350)
    # m = create_fancy_graph_map(
    #     graph=G.subgraph(nodes),
    #     outfile="data/nola_subgraph_map_5.html",
    #     edge_attr="mode",
    #     color_scheme={"transit": "red", "walk": "blue"},
    # )
    #
    # import matplotlib.pyplot as plt
    #
    # networkx.draw(G.subgraph(nodes))
    # plt.draw()  # pyplot draw()
    # plt.show()

    print("stop")
