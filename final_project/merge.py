"""merge.py

WIP - This method is borrowed and needs to be refactored with
Network.open_as_edges_df() Context manager
"""


def convert_length_to_meter(walk_graph):
    """
    Helper method for processing the WalkGraph and adding it to the transit network.
    
    This is a WIP! To be refactored using Network.open_as_edges_df()
    
    Attribution: from http://kuanbutts.com/2018/12/24/peartree-with-walk-network/
    
    Args:
        walk_graph (WalkNetwork.G): 

    Returns:
        Modified walk_graph with "length" changed from meters to seconds and boarding_cost=0
    """

    # TODO refactor with Network.open_as_edges_df()

    walk_speed = 4.5  # about 3 miles per hour

    # Iterate through and convert lengths to seconds
    for from_node, to_node, edge in walk_graph.edges(data=True):
        orig_len = edge["length"]

        # Note that this is a MultiDiGraph so there could
        # be multiple indices here, I naively assume this is not
        # the case
        walk_graph[from_node][to_node][0]["orig_length"] = orig_len

        # Conversion of walk speed and into seconds from meters
        kmph = (orig_len / 1000) / walk_speed
        in_seconds = kmph * 60 * 60
        walk_graph[from_node][to_node][0]["length"] = in_seconds

        # And state the mode, too
        walk_graph[from_node][to_node][0]["mode"] = "walk"

    # So this should be easy - just go through all nodes
    # and make them have a 0 cost to board
    for i, node in walk_graph.nodes(data=True):
        walk_graph.nodes.get(i)["boarding_cost"] = 0

    return walk_graph
