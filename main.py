import ctypes
import time

import cv2
import mss
import numpy as np
from win32gui import FindWindow, GetWindowRect

if __name__ == '__main__':
    print("Hello, world!")
    # DPI Scaling workaround from
    # https://stackoverflow.com/questions/44398075/can-dpi-scaling-be-enabled-disabled-programmatically-on-a-per-session-basis
    # This works for Win10/8 but not 7/Vista
    errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)

    crop_x = 1480
    crop_y = 747
    # Homography from https://learnopencv.com/homography-examples-using-opencv-python-c/
    # Hardcoded points for homography :)
    pts_src = np.array([[1724-crop_x,883-crop_y],
                        [1744-crop_x,953-crop_y],
                        [1637-crop_x,953-crop_y],
                        [1657-crop_x,883-crop_y]])
    pts_dst = np.array([[1006,863], [1006,981], [911,981], [911,863]])
    h, status = cv2.findHomography(pts_src, pts_dst)

    window_handle = FindWindow(None, "Euro Truck Simulator 2")

    with mss.mss() as sct:
        last_time = time.time()
        while True:
            # grab window position
            # assuming you're using Win10 + ETS2 in 1920x1080 window
            window_rect = GetWindowRect(window_handle)
            ets2_window = {"top": window_rect[1]+crop_y,
                        "left": window_rect[0]+10+crop_x, # no clue why
                        "width": 1921-crop_x,
                        "height": 1120-crop_y
                        }
            im_src = np.array(sct.grab(ets2_window))
            im_out = cv2.warpPerspective(im_src, h, (1921, 1120))

            cv2.imshow('Source Image', im_src)
            cv2.imshow("Warped Source Image", im_out)

            print(f'FPS: {1/(time.time()-last_time)}')
            last_time = time.time()
            # Press "q" to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
    # end of loop