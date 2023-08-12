# imgproc.py
# contains constants and functions for inferring centreline from an image
import cv2
import numpy as np
# from skimage.morphology import medial_axis

# hardcoded colours for drawing
RED = (0, 0, 255)
BLUE = (255, 0, 0)
CYAN = (255, 255, 0)
WHITE_1CH = (255)

# hardcoded GPS colours, remember its BGRA not RGBA
GREEN_MIN = (6, 229, 17, 255)
GREEN_MAX = (28, 251, 97, 255)
RED_MIN = (11, 11, 194, 255)
RED_MAX = (42, 42, 207, 255)

# for morphology closing to remove driver icon from GPS
KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

# window size of 1920x1080 ETS2 windowed
# TODO: adapt to fullscreen or diff window sizes
# TODO: also adapt if truck is right-hand drive (in which case GPS is in the left corner)
WIN_WIDTH = 1921
WIN_HEIGHT = 1120
# offset to GPS window (in the bottom right)
CROP_X = 1480
CROP_Y = 747
# Homography from https://learnopencv.com/homography-examples-using-opencv-python-c/
# Hardcoded points for homography :)
PTS_SRC = np.array([[1724-CROP_X,883-CROP_Y],
                    [1744-CROP_X,953-CROP_Y],
                    [1637-CROP_X,953-CROP_Y],
                    [1657-CROP_X,883-CROP_Y]])
PTS_DST = np.array([[1006,863], [1006,981], [911,981], [911,863]])
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
    im_out = cv2.warpPerspective(im_src, HOMOGRAPHY, (WIN_WIDTH, WIN_HEIGHT), flags=cv2.INTER_NEAREST)
    # thinned = cv2.ximgproc.thinning(comb_mask)
    # thin_warp = cv2.warpPerspective(thinned, h, (WIN_WIDTH, WIN_HEIGHT), flags=cv2.INTER_NEAREST)
    # thin_warp = cv2.cvtColor(thin_warp, cv2.COLOR_GRAY2BGRA)
    # im_out = cv2.bitwise_or(im_out, thin_warp)

    # get contours of path
    contours, heirarchy = cv2.findContours(comb_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
    comb_mask = cv2.cvtColor(comb_mask, cv2.COLOR_GRAY2BGRA)

    # approximation not needed, I can't seem to tune it
    # to a nice value
    """
    approx = []
    for contour in contours:
        epsilon = 0.001 * cv2.arcLength(contour, True)
        approx.append(cv2.approxPolyDP(contour, epsilon, True))
    # """
    # draw on og HUD
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
        for point in contour:
            cv2.drawMarker(im_out, point[0], BLUE, cv2.MARKER_TILTED_CROSS, 5)

    # thinning not working so we're abandoning it
    """
    # perform thinning -> convert to polyline on top-down contours
    topdown = np.zeros((WIN_HEIGHT, WIN_WIDTH), np.uint8)
    cv2.drawContours(topdown, warped_contours, -1, WHITE_1CH, cv2.FILLED)
    # performance optimisation: crop to bounding box in preparation for thinning
    cont_top, cont_left = WIN_HEIGHT, WIN_WIDTH
    cont_bottom, cont_right = 0, 0
    # find the overall bounding box of each contour
    for contour in warped_contours:
        x, y, w, h = cv2.boundingRect(contour)
        cont_top = max(min(cont_top, y), 0)
        cont_left = max(min(cont_left, x), 0)
        cont_bottom = min(max(cont_bottom, y+h), WIN_HEIGHT)
        cont_right = min(max(cont_right, x+w), WIN_WIDTH)
    topdown = topdown[cont_top:cont_bottom, cont_left:cont_right]
    if len(warped_contours) > 0:
        # image thinning
        # this bit is very laggy - varies between 3-15fps
        topdown = cv2.ximgproc.thinning(topdown)
        # topdown = medial_axis(topdown, rng=0)
        # topdown = 255 * topdown.astype(np.uint8)
        topdown = cv2.copyMakeBorder(topdown,
                                    cont_top,
                                    WIN_HEIGHT - cont_bottom,
                                    cont_left,
                                    WIN_WIDTH - cont_right,
                                    cv2.BORDER_CONSTANT, (0))
        topdown = cv2.cvtColor(topdown, cv2.COLOR_GRAY2BGRA)
        im_out = cv2.bitwise_or(im_out, topdown)
    # """
    cv2.imshow('Mask', comb_mask)
    # cv2.imshow('Thinned', thinned)
    cv2.imshow('Warped Source Image', im_out)