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
CROP_Y = 747
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

    # obtain via triangulating the contour instead:
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
    for contour in warped_contours:
        if cv2.pointPolygonTest(contour, TRUCK_CENTRE, measureDist=False) == 1:
            start_contour = contour
            break

    # 2. get left/right contour points to start
    # might need to change this algo a bit, for some edge cases
    # reminder: coordinate format is (x,y) -> [0,1]
    if start_contour is not None:
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
        if left_idx != -1 and right_idx != -1:
            # starting points found, we can continue
            # otherwise we're probably outside the line

            # for now just draw on the final image
            cv2.drawMarker(
                im_out, start_contour[left_idx][0], YELLOW, cv2.MARKER_STAR, 5
            )
            cv2.drawMarker(
                im_out, start_contour[right_idx][0], YELLOW, cv2.MARKER_STAR, 5
            )

    cv2.imshow("Source Image", im_src)
    cv2.imshow("Mask", comb_mask)
    # cv2.imshow('Thinned', thinned)
    cv2.imshow("Warped Source Image", im_out)
    return warped_contours, im_out
