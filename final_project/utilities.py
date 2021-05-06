from osmnx import projection, utils_graph, distance
import numpy
from networkx.algorithms.shortest_paths.generic import shortest_path, has_path

from pyproj import CRS

# scipy and sklearn are optional dependencies for faster nearest node search
try:
    from scipy.spatial import cKDTree
except ImportError:
    cKDTree = None
try:
    from sklearn.neighbors import BallTree
except ImportError:
    BallTree = None
EARTH_RADIUS_M = 6_371_009


def is_projected(crs):
    """
    Determine if a coordinate reference system is projected or not.
    This is a convenience wrapper around the pyproj.CRS.is_projected function.
    Parameters
    ----------
    crs : string or pyproj.CRS
        the coordinate reference system
    Returns
    -------
    projected : bool
        True if crs is projected, otherwise False
    """
    return CRS.from_user_input(crs).is_projected


def nearest_k_nodes(G, X, Y, k=1, return_dist=False):
    """
    Find the nearest node(s) to some point(s).
    If the graph is projected, this uses a k-d tree for euclidean nearest
    neighbor search, which requires that scipy is installed as an optional
    dependency. If it is unprojected, this uses a ball tree for haversine
    nearest neighbor search, which requires that scikit-learn is installed as
    an optional dependency.
    Parameters
    ----------
    G : networkx.MultiDiGraph
        graph in which to find nearest nodes
    X : float or numpy.array
        points' x or longitude coordinates, in same CRS/units as graph and
        containing no nulls
    Y : float or numpy.array
        points' y or latitude coordinates, in same CRS/units as graph and
        containing no nulls
    return_dist : bool
        optionally also return distance between points and nearest nodes
    Returns
    -------
    nn or (nn, dist)
        nearest node IDs or optionally a tuple where `dist` contains distances
        between the points and their nearest nodes
    """
    is_scalar = False
    if not (hasattr(X, "__iter__") and hasattr(Y, "__iter__")):
        # make coordinates arrays if user passed non-iterable values
        is_scalar = True
        X = numpy.array([X])
        Y = numpy.array([Y])

    if numpy.isnan(X).any() or numpy.isnan(Y).any():  # pragma: no cover
        raise ValueError("`X` and `Y` cannot contain nulls")
    nodes = utils_graph.graph_to_gdfs(G, edges=False, node_geometry=False)[["x", "y"]]

    if is_projected(G.graph["crs"]):
        # if projected, use k-d tree for euclidean nearest-neighbor search
        if cKDTree is None:  # pragma: no cover
            raise ImportError("scipy must be installed to search a projected graph")
        dist, pos = cKDTree(nodes).query(numpy.array([X, Y]).T, k=k)
        nn = nodes.index[pos]

    else:
        # if unprojected, use ball tree for haversine nearest-neighbor search
        if BallTree is None:  # pragma: no cover
            raise ImportError(
                "scikit-learn must be installed to search an unprojected graph"
            )
        # haversine requires lat, lng coords in radians
        nodes_rad = numpy.deg2rad(nodes[["y", "x"]])
        points_rad = numpy.deg2rad(numpy.array([Y, X]).T)
        [dist], [pos] = BallTree(nodes_rad, metric="haversine").query(points_rad, k=k)
        dist = dist * EARTH_RADIUS_M  # convert radians -> meters
        nn = nodes.index[pos]

    # convert results to correct types for return
    nn = nn.tolist()
    dist = dist.tolist()
    if is_scalar:
        nn = nn[:k]
    #         dist = [dist[p] for p in pos]

    if return_dist:
        return nn, dist
    else:
        return nn


def get_route_length(graph, route):
    length = 0
    first_node = route[0]
    for node in route[1:]:
        length = length + graph[first_node][node][0]["length"]
        first_node = node
    return length


def get_shortest_pair(graph, origin, dest, k=3):

    nearest_to_a, _ = nearest_k_nodes(
        graph, origin[1], origin[0], k=k, return_dist=True
    )
    nearest_to_b, _ = nearest_k_nodes(graph, dest[1], dest[0], k=k, return_dist=True)

    shortest_dist = 1000000000000
    shortest_route = None

    for a in nearest_to_a:
        for b in nearest_to_b:
            #             print(a, b, "a and b")
            try:
                route = shortest_path(graph, a, b)
                #                 print(len(route), "len")
                dist = get_route_length(graph, route)
                #                 print(dist, "dist")
                if dist < shortest_dist:
                    shortest_dist = dist
                    shortest_route = route
            except:
                pass
    if shortest_route:
        return (shortest_route, shortest_dist)
    else:
        raise RuntimeError("No shortest path")
