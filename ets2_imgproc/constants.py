import cv2
import numpy as np

# hardcoded colours for drawing
RED = (0, 0, 255)
BLUE = (255, 0, 0)
DARK_GREEN = (0, 127, 0)
CYAN = (255, 255, 0)
YELLOW = (0, 255, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
WHITE_1CH = 255

# hardcoded GPS thresholding colours, remember its BGRA not RGBA
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
