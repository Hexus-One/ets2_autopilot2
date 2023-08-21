# imgproc.py
# contains constants and functions for inferring centreline from an image
import cv2
import numpy as np
import triangle as tr

# from skimage.morphology import medial_axis

# hardcoded colours for drawing
RED = (0, 0, 255)
BLUE = (255, 0, 0)
DARK_GREEN = (0, 127, 0)
CYAN = (255, 255, 0)
YELLOW = (0, 255, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
WHITE_1CH = 255

# hardcoded GPS colours, remember its BGRA not RGBA
GREEN_MIN = (6, 229, 17, 255)
GREEN_MAX = (28, 251, 97, 255)
RED_MIN = (11, 11, 194, 255)
RED_MAX = (42, 42, 207, 255)

# for morphological operations e.g. closing to remove driver icon from GPS
KERNEL3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
KERNEL5 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

# window size of 1920x1080 ETS2 windowed
# TODO: adapt to fullscreen or diff window sizes
# TODO: also adapt if truck is right-hand drive
#       (in which case GPS is in the left corner)
WIN_WIDTH = 1921
WIN_HEIGHT = 1120
# offset to GPS window (in the bottom right)
CROP_X = 1480
CROP_Y = 800
# Homography from https://learnopencv.com/homography-examples-using-opencv-python-c/
# Hardcoded points for homography :)
PTS_SRC = np.array(
    [
        [1724 - CROP_X, 883 - CROP_Y],
        [1744 - CROP_X, 953 - CROP_Y],
        [1637 - CROP_X, 953 - CROP_Y],
        [1657 - CROP_X, 883 - CROP_Y],
    ]
)
PTS_DST = np.array([[1006, 863], [1006, 981], [911, 981], [911, 863]])
TRUCK_CENTRE = (958.5, 922)  # centre of truck in top-down view
# getPerspectiveTransform would also work here
HOMOGRAPHY, status = cv2.findHomography(PTS_SRC, PTS_DST)


def infer_polyline(im_src):
    """Takes an image from the GPS HUD and returns the centreline of the route."""
    # masking and warping to obtain top-down view of route
    # binary threshold of the red and green pixels
    green_mask = cv2.inRange(im_src, GREEN_MIN, GREEN_MAX)
    red_mask = cv2.inRange(im_src, RED_MIN, RED_MAX)
    comb_mask = cv2.bitwise_or(green_mask, red_mask)
    # remove holes caused by player truck icon
    comb_mask = cv2.morphologyEx(comb_mask, cv2.MORPH_CLOSE, KERNEL5)
    # don't use morph_open with 3x3 kernel as it eliminates 1-pixel lines near top of image
    # we'd rather deal with single-pixel dots from speed limit signs
    # comb_mask_inv = cv2.bitwise_not(comb_mask)
    # im_src = cv2.bitwise_and(im_src, im_src, mask=comb_mask_inv)
    im_out = cv2.warpPerspective(
        im_src, HOMOGRAPHY, (WIN_WIDTH, WIN_HEIGHT), flags=cv2.INTER_NEAREST
    )

    # get contours of path
    contours, heirarchy = cv2.findContours(
        comb_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS
    )

    # approximation not needed, I can't seem to tune it to a nice value
    """
    approx = []
    for contour in contours:
        epsilon = 0.001 * cv2.arcLength(contour, True)
        approx.append(cv2.approxPolyDP(contour, epsilon, True))
    # """
    # draw on og HUD
    comb_mask = cv2.cvtColor(comb_mask, cv2.COLOR_GRAY2BGRA)
    cv2.drawContours(comb_mask, contours, -1, RED, 1)

    # warp contours for transformed perspective
    warped_contours = []
    for contour in contours:
        # discard degenerate contours that probably don't represent road
        # if contour.size < 5:
        #     continue
        contourf = contour.astype(np.float32)
        warped_cont = cv2.perspectiveTransform(contourf, HOMOGRAPHY)
        warped_contours.append(warped_cont.astype(int))

    # abandoned thinning via centreline
    # takes too long (like 2-20fps in pure python)
    centreline, diagonals = contours_to_centreline(warped_contours, heirarchy)

    for line in diagonals:
        cv2.line(im_out, line[0].astype(int), line[1].astype(int), MAGENTA)
    cv2.drawContours(im_out, warped_contours, -1, CYAN, 1)
    # draw contour points
    for contour in warped_contours:
        for [point] in contour:
            cv2.drawMarker(im_out, point, BLUE, cv2.MARKER_TILTED_CROSS, 1)
    # no clue why this is needed but yeah
    # taken from https://www.geeksforgeeks.org/python-opencv-cv2-polylines-method/
    centreline_np = np.array(centreline, np.int32)
    centreline_np = centreline_np.reshape((-1, 1, 2))
    # draw centreline
    cv2.polylines(im_out, [centreline_np], False, YELLOW)

    # draw centreline points
    for point in centreline:
        cv2.drawMarker(
            im_out, point.astype(int), DARK_GREEN, cv2.MARKER_TILTED_CROSS, 1
        )

    if len(centreline) > 0:
        # offset so 0,0 is at truck centre
        centreline = np.subtract(centreline, TRUCK_CENTRE)
        # 180 degree rotation so that x+ is left and y+ is in front
        # 1/4 scale so 1 unit = 1 metre
        centreline = np.multiply(centreline, (-0.25, -0.25))

    cv2.imshow("Source Image", im_src)
    cv2.imshow("Mask", comb_mask)
    # cv2.imshow('Thinned', thinned)
    cv2.imshow("Warped Source Image", im_out)
    return centreline, im_out


def contours_to_centreline(contours, heirarchy):
    centreline = []  # list of points on centre
    diagonals = []  # list of pairs of points of diagonals (for debug)

    # obtain via triangulating the contour:
    # 1. find the contour the truck is inside
    # 2. use Constrained Delaunay Triangulation to obtain the diagonals
    # 3. draw points on the midpoint of every diagonal
    # 4. link points of diagonals between adjacent triangles to obtain ordering
    #  a. resolve crossovers by the following:
    #
    # 5. use green arrows to determine forward/reverse direction

    # 1. find containing contour
    start_idx = None
    start_contour = None
    for idx, contour in enumerate(contours):
        if cv2.pointPolygonTest(contour, TRUCK_CENTRE, measureDist=False) == 1:
            start_idx, start_contour = idx, contour
            break
    # check contour thickness (area:perimeter ratio) to determine if we're at the correct map zoom
    # for 1920x1080 window, thickness is ~20 zoomed in and ~10 zoomed out
    # arbitrary threshold here, probably need to scale to screen size later
    if start_contour is None or contour_thickness(start_contour) < 15:
        return centreline, diagonals

    # convert contour into a format suitable for Triangle package
    contour_tr = contourcv2_to_tr(start_idx, contours, heirarchy)
    triangulation = tr.triangulate(contour_tr, "pne")
    # obtain only the diagonals by concatenating edges and segments, then eliminating duplicates
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
    # In our application there should be only two children of a top-level contour at most
    # see tests/data/double_crossover.png
    N = len(contours[contour_idx])
    # create vertices and segments for top-level contour
    vertices = np.reshape(contours[contour_idx], (-1, 2))
    i = np.arange(N)
    segments = np.stack([i, i + 1], axis=1) % N
    # holes needs to have at least one element or it crashes :)
    # get the bounding rectangle and choose a point outside to guaruntee normal operation
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
        # use the middle of the bounding rectangle as hole location (should work in every case)
        x, y, w, h = cv2.boundingRect(contours[child_idx])
        holes.append([x + w / 2, y + h / 2])
        child_idx = heirarchy[0][child_idx][0]  # fetch the next child

    return dict(vertices=vertices, segments=segments, holes=holes)


def filter_jagged(centreline: list, angle):
    """Remove any corners in centreline with an angle < angle

    Intended use is to smooth out jagged points induced by green arrows from the image processing step
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


# from https://manivannan-ai.medium.com/find-the-angle-between-three-points-from-2d-using-python-348c513e2cd
def getAngleABC(a, b, c):
    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)


# compares abc to abd using triangle_metric, returns TRUE if abc is better than abd
def compare_triangles(idx_a, idx_b, idx_c, idx_d, contour):
    abc = triangle_metric(contour[idx_a], contour[idx_b], contour[idx_c])
    bad = triangle_metric(contour[idx_b], contour[idx_a], contour[idx_d])
    return abc >= bad


# triangle metric, higher is better
def triangle_metric(a, b, c):
    # trying negative diagonal length (i.e. shorter diag is better)
    return -diagonal_length(a, b, c)


def diagonal_length(a, b, c):
    return cv2.norm(b - c)


# reciprocal of aspect ratio of a triangle, i.e ratio of shortest:longest side
# a, b, c -> three points
def aspect_ratio(a, b, c):
    ab = cv2.norm(a - b)
    bc = cv2.norm(b - c)
    ac = cv2.norm(a - c)
    return min(ab, bc, ac) / max(ab, bc, ac)
