import cv2
import numpy as np
import triangle as tr

from .constants import TRUCK_CENTRE


def contours_to_centreline(contours, heirarchy):
    """Find the centreline of a set of contours.

    Current algorithm uses the closest contour to the truck,
    and assumes the truck is pointed mostly the right way.
    Based on [Chordal Axis Transform](https://github.com/NRCan/geo_sim_processing#chordal-axis)
    but using a greedy algorithm instead.
    """
    centreline = []  # list of points on centre
    diagonals = []  # list of pairs of points of diagonals (for debug)
    # centreline obtained via triangulating the contour:
    # 0. maintain a list of headings and weights (i.e. lengths)
    # 1. find the contour the truck is inside
    # 2. use Constrained Delaunay Triangulation (CDT) to obtain the diagonals
    # 3. find the containing triangle (hopefully there's just one)
    # 4. draw starting segment by connecting the midpoint of two of the-
    #    triangle's edges.
    # 5. Iterate through adjacent triangles and draw centreline through diagonals
    #    a. for junction triangles, choose the side that's more straight
    # 6. continue until terminal triangle (hopefully we don't get stuck on
    #    circular loops)

    # 1. find containing contour
    start_contour_idx = None
    start_contour = None
    for idx, contour in enumerate(contours):
        if cv2.pointPolygonTest(contour, TRUCK_CENTRE, measureDist=False) in (1, 0):
            start_contour_idx, start_contour = idx, contour
            break
    # check contour thickness (area:perimeter ratio) to determine if we're at
    # the correct map zoom.
    # for 1920x1080 window, thickness is ~20 zoomed in and ~10 zoomed out
    # arbitrary threshold here, probably need to scale to screen size later
    if start_contour is None or contour_thickness(start_contour) < 15:
        return centreline, diagonals

    # convert contour into a format suitable for Triangle package
    contour_tr = contourcv2_to_tr(start_contour_idx, contours, heirarchy)
    triangulation = tr.triangulate(contour_tr, "pne")
    # centreline via greedy walk through triangles
    headings = [(-90, 20)]  # (heading(deg), length), including initial direction
    triangle_idx = get_containing_triangle(TRUCK_CENTRE, triangulation)
    prev_tri_idx = triangle_idx  # for iteration
    normals = get_triangle_normals(triangle_idx, triangulation)
    match count_neighbours(triangle_idx, triangulation):
        case 0:  # Isolated triangle
            pass  # Skip to next bit
        case 1:  # Terminal triangle
            # Either the truck just started on the line (forwards)
            # or its aboutta head out.jpg (backwards)
            # add the midpoint of the first edge and one of the border edges,
            # depending on heading.
            # for neighbours [A, B, C], neighbour A shares vertices BC with
            # the current triangle.
            # funny unpacking required to get int out of (array([]))
            neighbour = np.nonzero(triangulation["neighbors"][triangle_idx] != -1)[0][0]
            midpoint_neighbour = get_midpoint(neighbour, triangle_idx, triangulation)
            # two cases for forwards- and backwards- facing terminal triangle
            # get the opposite edge (facing most backwards/fowards respectively)
            # no need to eliminate the existing edge - mathematically impossible
            # to choose it again.
            if abs(normals[neighbour]) <= 90:
                opposite = np.argmax(abs(normals))  # forwards
            else:
                opposite = np.argmin(abs(normals))  # backwards
            midpoint_border = get_midpoint(opposite, triangle_idx, triangulation)
            if abs(normals[neighbour]) <= 90:  # insert depending on fwd/bck
                centreline = [midpoint_border, midpoint_neighbour]  # fwd
                triangle_idx = triangulation["neighbors"][triangle_idx][neighbour]
            else:
                centreline = [midpoint_neighbour, midpoint_border]  # bck
                triangle_idx = -1
        case 2:  # Sleeve triangle
            # add midpoints of the two edges, use heading to determine direction
            neighbours = np.nonzero(triangulation["neighbors"][triangle_idx] != -1)[0]
            # figure out which side is front/back
            # BUG: something is messing up here
            # are triangle vertices always clockwise?
            fwd = neighbours[np.argmin(normals[neighbours])]
            bck = neighbours[np.argmax(normals[neighbours])]
            second = get_midpoint(fwd, triangle_idx, triangulation)
            first = get_midpoint(bck, triangle_idx, triangulation)
            centreline = [first, second]
            triangle_idx = triangulation["neighbors"][triangle_idx][fwd]
        case 3:  # Junction triangle
            # similar to sleeve but use the two edges that face the most towards
            # the truck, i.e. exclude the "side" edge
            pass
    # iterate thru triangles until terminal
    while triangle_idx != -1:
        normals = get_triangle_normals(triangle_idx, triangulation)
        match count_neighbours(triangle_idx, triangulation):
            case 0:  # Isolated triangle
                break  # Escape and just return an empty centreline
            case 1:  # Terminal triangle
                # add midpoint of border edge with closest heading
                break
            case 2:  # Sleeve triangle
                # add the next point
                neighbour = np.nonzero(  # more funny unpacking
                    np.logical_and(
                        triangulation["neighbors"][triangle_idx] != -1,
                        triangulation["neighbors"][triangle_idx] != prev_tri_idx,
                    )
                )[0][0]
                centreline.append(get_midpoint(neighbour, triangle_idx, triangulation))
                prev_tri_idx = triangle_idx
                triangle_idx = triangulation["neighbors"][triangle_idx][neighbour]
            case 3:  # Junction triangle
                # use weighted heading to determine which triangle to choose
                break
        # might need something to protect against circular loops like a length
        # check.
        if len(centreline) >= 2:  # update headings
            segment = centreline[-1] - centreline[-2]
            heading = np.degrees(np.arctan2(*np.flip(segment)))
            weight = cv2.norm(segment)  # could also use
            headings.append((heading, weight))

    # diagonals might not be needed at all, just for debug display
    # obtain only the diagonals via set difference
    edges = np.sort(triangulation["edges"])
    segments = np.sort(triangulation["segments"])
    for edge in setdiff2d_bc(edges, segments):
        diagonals.append(
            (
                triangulation["vertices"][edge[0]],
                triangulation["vertices"][edge[1]],
            )
        )
    # filter_jagged(centreline, 100)
    return centreline, diagonals


def count_neighbours(idx: int, triangulation: dict):
    """Given a triangle, return the number of neighbours.

    Reminder: our function has British English spelling but the Triangle library
    has American English spelling :)"""
    return np.count_nonzero(triangulation["neighbors"][idx] != -1)


def get_triangle_normals(idx: int, triangulation: dict) -> list[float, float, float]:
    """Given a triangle, return the normals of its edges (outwards).

    Output is in degrees [-180,180], with 0 degrees at x=0, y- axis.
    Edge ordering for a triangle [A,B,C] is [bc, ca, ab]."""
    # index format is not always clockwise so we need to flip
    #   (in computer graphics coordinate system, x+ right y+ down)
    # using maths coordinate system (x+ right, y+ up) it's anti-clockwise
    vertices = triangulation["vertices"][triangulation["triangles"][idx]]  # [A,B,C]
    vert_rolled = np.roll(vertices, -1, 0)  # [B, C, A]
    vert_rolled2 = np.roll(vertices, 1, 0)  # [C, A, B]
    offsets = vert_rolled2 - vert_rolled  # [bc, ca, ab]
    if np.cross(*offsets[0:2]) < 0: # flip if anti-clockwise
        offsets = -offsets
    offsets = np.flipud(np.transpose(offsets))  # reshape for atan2
    normals = np.degrees(np.arctan2(*offsets))
    return normals


def get_tri_angles_atan2(triangle: list[float, float, float]) -> float:
    """Get angle at b using np.atan2

    Output in degrees. (basically used to check if a triangle is clockwise
    or anti-clockwise)"""
    points_rolled = np.roll(triangle, -1, 0)
    points_rolled2 = np.roll(triangle, 1, 0)
    lines = points_rolled2 - points_rolled
    headings = np.arctan2(*np.flipud(np.transpose(lines)))
    headings_rolled = np.roll(headings, 1, 0)
    return np.degrees(np.unwrap(headings - headings_rolled))


def get_midpoint(
    vertex_idx: int, triangle_idx: int, triangulation: dict
) -> list[float, float]:
    """Given a triangle, get the midpoint of its edge opposite the vertex."""
    # get the corresponding edge
    vertex_indices = np.delete(triangulation["triangles"][triangle_idx], vertex_idx, 0)
    vertices = triangulation["vertices"][vertex_indices]
    return np.mean(vertices, 0)


def get_containing_triangle(point: tuple[float, float], triangulation: dict) -> int:
    """Given a triangulation and point, return the index of the triangle containing the point."""
    for idx, triangle in enumerate(triangulation["triangles"]):
        vertices = triangulation["vertices"][triangle].astype(np.float32)
        # check bounding box first before using point polygon test for performance.
        # (1, 0) corresponds to either inside or on the edge respectively
        if point_in_bbox(
            cv2.boundingRect(vertices), TRUCK_CENTRE
        ) and cv2.pointPolygonTest(vertices, TRUCK_CENTRE, False) in (1, 0):
            return idx


def point_in_bbox(rect, point: tuple[float, float]) -> bool:
    """Check if a point is inside a given rectangle."""
    return (
        rect[0] <= point[0] <= rect[0] + rect[2]
        and rect[1] <= point[1] <= rect[1] + rect[3]
    )


def setdiff2d_bc(arr1, arr2):
    """Set difference of two arrays, i.e. arr1 - arr2

    From https://stackoverflow.com/a/66674679"""
    idx = (arr1[:, None] != arr2).any(-1).all(1)
    return arr1[idx]


def contour_thickness(contour):
    """Get the thickness of a curvilinear contour.

    Works best with long, windy shapes"""
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    return area / perimeter


def contourcv2_to_tr(contour_idx, contours, heirarchy):
    """Convert an OpenCV contour and its children to Triangle data format"""
    # In our application there should be only two children of a top-level
    # contour at most - see tests/data/double_crossover.png
    N = len(contours[contour_idx])
    # create vertices and segments for top-level contour
    vertices = np.reshape(contours[contour_idx], (-1, 2))
    i = np.arange(N)
    segments = np.stack([i, i + 1], axis=1) % N
    # holes needs to have at least one element or it crashes :)
    # get the bounding rectangle and choose a point outside
    x, *_ = cv2.boundingRect(contours[contour_idx])
    holes = [[x - 1, 0]]
    # iterate through children using the heirarchy table and append them
    # TODO: there's probably a more pythonic way to do this
    child_idx = heirarchy[0][contour_idx][2]
    while child_idx != -1:
        N = len(contours[child_idx])
        child_verts = np.reshape(contours[child_idx], (-1, 2))
        vertices = np.vstack([vertices, child_verts])
        i = np.arange(N)
        child_segments = np.stack([i, i + 1], axis=1) % N
        segments = np.vstack([segments, child_segments + len(segments)])
        # use the middle of the bounding rectangle as hole location
        # (should work in every case)
        x, y, w, h = cv2.boundingRect(contours[child_idx])
        holes.append([x + w / 2, y + h / 2])
        child_idx = heirarchy[0][child_idx][0]  # fetch the next child

    return dict(vertices=vertices, segments=segments, holes=holes)


def filter_jagged(centreline: list, angle):
    """Remove any corners in centreline with an angle < angle

    Intended use is to smooth out jagged points induced by green arrows from
    the image processing step.
    """
    # TODO: something is wrong with this I'm pretty sure
    # probably not efficient
    # worst case O(n^2) if somehow every point gets removed

    # loop through the whole list until there are no more points to remove
    compliant = False
    pts_removed = 0
    while not compliant:
        # iterate through list in triplets, remove middle if violating
        compliant = True
        for i in range(len(centreline) - 2):
            if (
                getAngleABC(centreline[i], centreline[i + 1], centreline[i + 2])
                <= angle
            ):
                centreline.pop(i + 1)
                pts_removed += 1
                compliant = False
                break
    return centreline


def getAngleABC(a, b, c) -> float:
    """From https://manivannan-ai.medium.com/find-the-angle-between-three-points-from-2d-using-python-348c513e2cd

    Output in degrees."""
    # numpy implementation is slightly slower than maths :)
    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)


def compare_triangles(idx_a, idx_b, idx_c, idx_d, contour):
    """Compares abc to abd using triangle_metric.

    Returns True if abc is better than abd."""
    abc = triangle_metric(contour[idx_a], contour[idx_b], contour[idx_c])
    bad = triangle_metric(contour[idx_b], contour[idx_a], contour[idx_d])
    return abc >= bad


def triangle_metric(a, b, c):
    """Triangle metric for choosing diagonals - higher is better"""
    # trying negative diagonal length (i.e. shorter diag is better)
    return -diagonal_length(a, b, c)


def diagonal_length(a, b, c):
    return cv2.norm(b - c)


def aspect_ratio(a, b, c):
    """Get the reciprocal of aspect ratio of a triangle,
    i.e ratio of shortest:longest side"""
    # a, b, c -> three points
    ab = cv2.norm(a - b)
    bc = cv2.norm(b - c)
    ac = cv2.norm(a - c)
    return min(ab, bc, ac) / max(ab, bc, ac)
