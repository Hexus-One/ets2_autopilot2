# imgproc.py
# contains constants and functions for inferring centreline from an image
import cv2
import numpy as np

# from skimage.morphology import medial_axis

# hardcoded colours for drawing
RED = (0, 0, 255)
BLUE = (255, 0, 0)
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

# for morphology closing to remove driver icon from GPS
KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

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
    # masking and warping to obtain top-down view of route
    green_mask = cv2.inRange(im_src, GREEN_MIN, GREEN_MAX)
    red_mask = cv2.inRange(im_src, RED_MIN, RED_MAX)
    comb_mask = cv2.bitwise_or(green_mask, red_mask)
    comb_mask = cv2.morphologyEx(comb_mask, cv2.MORPH_CLOSE, KERNEL)
    comb_mask_inv = cv2.bitwise_not(comb_mask)
    im_tmp3 = cv2.bitwise_and(im_src, im_src, mask=comb_mask_inv)
    im_out = cv2.warpPerspective(
        im_src, HOMOGRAPHY, (WIN_WIDTH, WIN_HEIGHT), flags=cv2.INTER_NEAREST
    )
    # thinned = cv2.ximgproc.thinning(comb_mask)
    # thin_warp = cv2.warpPerspective(thinned, h, (WIN_WIDTH, WIN_HEIGHT), flags=cv2.INTER_NEAREST)
    # thin_warp = cv2.cvtColor(thin_warp, cv2.COLOR_GRAY2BGRA)
    # im_out = cv2.bitwise_or(im_out, thin_warp)
    # comb_mask = cv2.GaussianBlur(comb_mask, (5, 5), 0)
    # get contours of path
    contours, heirarchy = cv2.findContours(
        comb_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS
    )

    # approximation not needed, I can't seem to tune it
    # to a nice value
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
        if contour.size < 5:
            continue
        contourf = contour.astype(np.float32)
        warped_cont = cv2.perspectiveTransform(contourf, HOMOGRAPHY)
        warped_contours.append(warped_cont.astype(int))
    cv2.drawContours(im_out, warped_contours, -1, CYAN, 1)
    for contour in warped_contours:
        for [point] in contour:
            cv2.drawMarker(im_out, point, BLUE, cv2.MARKER_TILTED_CROSS, 5)

    # abandoned thinning via centreline
    # takes too long (like 2-20fps in pure python)
    centreline, diagonals = contours_to_centreline(warped_contours)

    for line in diagonals:
        cv2.line(im_out, line[0], line[1], MAGENTA)
    # no clue why this is needed but yeah
    # taken from https://www.geeksforgeeks.org/python-opencv-cv2-polylines-method/
    centreline_np = np.array(centreline, np.int32)
    centreline_np = centreline_np.reshape((-1, 1, 2))
    cv2.polylines(im_out, [centreline_np], False, YELLOW)

    for point in centreline:
        cv2.drawMarker(im_out, point.astype(int), BLUE, cv2.MARKER_TILTED_CROSS, 1)

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


def contours_to_centreline(contours):
    centreline = []  # list of points on centre
    diagonals = []  # list of pairs of points of diagonals (for debug)

    # obtain via triangulating the contour:
    # 1. find the contour the truck is inside
    # 2. get the contour points to the left/right that are furthest up
    #     BUT below the truck, i.e. >= TRUCK_CENTRE.y
    #     i.e. with lowest y-coord
    # 3. draw a line between them (imaginary) and mark centrepoint
    # 4. walk upwards and add diagonals that have the least skewed triangle
    #     and add centrepoints to list
    # 5. proceed until ??

    # 1. find containing contour
    start_contour = None
    for contour in contours:
        if cv2.pointPolygonTest(contour, TRUCK_CENTRE, measureDist=False) == 1:
            start_contour = contour
            break

    # 2. get left/right contour points to start
    # might need to change this algo a bit, for some edge cases
    # reminder: coordinate format is (x,y) -> [0,1]

    if start_contour is None:
        return centreline, diagonals

    left_min = right_min = WIN_HEIGHT
    left_idx = right_idx = -1
    for idx, [point] in enumerate(start_contour):
        if point[1] < TRUCK_CENTRE[1]:  # only consider if below truck
            continue
        if point[0] < TRUCK_CENTRE[0]:  # to the left
            if point[1] < left_min:
                left_min = point[1]
                left_idx = idx
        else:  # to the right
            if point[1] < right_min:
                right_min = point[1]
                right_idx = idx

    if left_idx == -1 or right_idx == -1:
        return centreline, diagonals

    # starting points found, we can continue
    # otherwise we're probably outside the line

    # 3/4/5 do the walking thing
    # as far as I know, contours go clockwise (at least the top-level
    # ones do) so we walk forwards for left, and backwards for right
    #   turns out its the opposite?? no clue why
    curr_L, curr_R = left_idx, right_idx
    while True:
        centre = (start_contour[curr_L][0] + start_contour[curr_R][0]) / 2
        centreline.append(centre)
        diagonals.append((start_contour[curr_L][0], start_contour[curr_R][0]))
        # two candidates for triangles
        cand_L = (curr_L - 1) % len(start_contour)
        cand_R = (curr_R + 1) % len(start_contour)
        # I guess we stop if we've looped around the contour?
        if cand_R == curr_L or cand_L == curr_R:
            break
        # compare the two triangles and add the "better" diagonal (metric TBD)
        if compare_triangles(curr_L, curr_R, cand_L, cand_R, start_contour):
            # left diagonal better
            curr_L = cand_L
        else:
            # right is better
            curr_R = cand_R
    centreline = filter_jagged(centreline, 100)
    return centreline, diagonals


def filter_jagged(centreline: list, angle):
    """Remove any corners in centreline with an angle > angle"""
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
    print(pts_removed)
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
