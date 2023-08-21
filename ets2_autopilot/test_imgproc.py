# test_imgproc.py
# run imgproc on test files and preview output

import ctypes
import os
from sys import platform

import cv2

from imgproc import infer_polyline, CROP_X, CROP_Y, WIN_HEIGHT, WIN_WIDTH

FOLDER = r".\tests\data"
OUTPUT = r".\tests\output"


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
        fullpath = os.path.join(FOLDER, filename)
        print(f"Opening {fullpath}")
        img = cv2.imread(fullpath)
        if img is None:
            continue

        cropped = img[CROP_Y:WIN_HEIGHT, CROP_X:WIN_WIDTH]
        _, im_out = infer_polyline(cropped)

        outname = os.path.join(OUTPUT, filename)
        cv2.waitKey(1)
        cv2.imwrite(outname, im_out)
