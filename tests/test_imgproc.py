# test_imgproc.py
# run imgproc on test files and preview output

import ctypes
import os
from sys import platform

import cv2

from .constants import *
from ets2_imgproc import infer_polyline, CROP_X, CROP_Y, WIN_HEIGHT, WIN_WIDTH


def test_imgproc():
    if platform == "win32":
        errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)

    # create a folder if it doesn't already exist
    try:
        os.mkdir(OUTPUT)
    except FileExistsError:
        pass

    # loop through images and process one at a time
    # TODO: refactor this test as a function that operates on one image
    for filename in os.listdir(FOLDER):
        if not filename.endswith(".png"):
            continue
        fullpath = os.path.join(FOLDER, filename)
        print(f"Opening {fullpath}")
        img = cv2.imread(fullpath)
        if img is None:
            continue
        # don't crop if already correct size
        if img.shape[0] == WIN_HEIGHT - CROP_Y:
            cropped = img
        else:
            cropped = img[CROP_Y:WIN_HEIGHT, CROP_X:WIN_WIDTH]

        try:
            _, im_out = infer_polyline(cropped)
        except Exception as inst:
            cv2.waitKey(1)
            raise inst
        else:
            outname = os.path.join(OUTPUT, filename)
            cv2.imwrite(outname, im_out)
        finally:
            cv2.waitKey(1)
