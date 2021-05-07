from networkx.readwrite import write_gpickle, read_gpickle
import osmnx as ox
import peartree as pt


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


def combine(NOLA_WALKING_PICKLE, NOLA_GTFS_ZIP, COMBINED_GRAPH_PICKLE):
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
    G2 = pt.load_feed_as_graph(
        feed, start, end, existing_graph=Gwalk_adj, impute_walk_transfers=True
    )
    G = cleanup_graph(G2)
    # ----- END COMBINE BLOCK -----

    write_gpickle(G, COMBINED_GRAPH_PICKLE)
