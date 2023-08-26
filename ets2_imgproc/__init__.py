"""
Contains constants and functions for inferring centreline from an image.
"""
import cv2
import numpy as np

from .constants import *
from .contours_to_centreline import contours_to_centreline


def infer_polyline(im_src):
    """Takes an image from the GPS HUD and returns the centreline of the route."""
    # masking and warping to obtain top-down view of route
    # binary threshold of the red and green pixels
    green_mask = cv2.inRange(im_src, GREEN_MIN, GREEN_MAX)
    red_mask = cv2.inRange(im_src, RED_MIN, RED_MAX)
    comb_mask = cv2.bitwise_or(green_mask, red_mask)
    # remove holes caused by player truck icon
    comb_mask = cv2.morphologyEx(comb_mask, cv2.MORPH_CLOSE, KERNEL5)
    # don't use morph_open with 3x3 kernel as it eliminates 1-pixel lines near
    # top of image - we'd rather deal with single-pixel dots from speed limit signs.
    # comb_mask_inv = cv2.bitwise_not(comb_mask)
    # im_src = cv2.bitwise_and(im_src, im_src, mask=comb_mask_inv)
    im_out = cv2.warpPerspective(
        im_src, HOMOGRAPHY, (WIN_WIDTH, WIN_HEIGHT), flags=cv2.INTER_NEAREST
    )

    # get contours of path
    contours, heirarchy = cv2.findContours(
        comb_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS
    )
    # draw on og HUD
    comb_mask = cv2.cvtColor(comb_mask, cv2.COLOR_GRAY2BGRA)
    cv2.drawContours(comb_mask, contours, -1, RED, 1)

    # warp contours for transformed perspective
    warped_contours = []
    for contour in contours:
        contourf = contour.astype(np.float32)
        warped_cont = cv2.perspectiveTransform(contourf, HOMOGRAPHY)
        warped_contours.append(warped_cont)

    # magic happens here :)
    centreline, diagonals = contours_to_centreline(warped_contours, heirarchy)

    # a heap of debug drawing
    for line in diagonals:
        cv2.line(im_out, line[0].astype(int), line[1].astype(int), MAGENTA)
    debug_contours = []
    for contour in warped_contours:
        contouri = contour.astype(int)
        debug_contours.append(contouri)
    cv2.drawContours(im_out, debug_contours, -1, CYAN, 1)
    for contour in debug_contours:  # draw contour points
        for [point] in contour:
            cv2.drawMarker(im_out, point, BLUE, cv2.MARKER_TILTED_CROSS, 1)
    # no clue why this conversion is needed but yeah
    # taken from https://www.geeksforgeeks.org/python-opencv-cv2-polylines-method/
    centreline_np = np.array(centreline, np.int32)
    centreline_np = centreline_np.reshape((-1, 1, 2))
    cv2.polylines(im_out, [centreline_np], False, YELLOW)  # draw centreline
    for point in centreline:  # draw centreline points
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
    cv2.imshow("Warped Source Image", im_out)
    return centreline, im_out
