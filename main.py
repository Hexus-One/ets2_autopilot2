import ctypes
import time

import cv2
import mss
import numpy as np

if __name__ == '__main__':
    print("Hello, world!")
    # DPI Scaling workaround from
    # https://stackoverflow.com/questions/44398075/can-dpi-scaling-be-enabled-disabled-programmatically-on-a-per-session-basis
    # This works for Win10/8 but not 7/Vista
    errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)

    # Homography from https://learnopencv.com/homography-examples-using-opencv-python-c/
    # Hardcoded points for homography :)
    pts_src = np.array([[1724,883], [1744,953], [1637,953], [1657,883]])
    pts_dst = np.array([[1006,863], [1006,981], [911,981], [911,863]])
    h, status = cv2.findHomography(pts_src, pts_dst)

    ets2_window = {"top": 140, "left": 319, "width": 1921, "height": 1120}

    with mss.mss() as sct:
        last_time = time.time()
        while True:
            im_src = np.array(sct.grab(ets2_window))

            im_out = cv2.warpPerspective(im_src, h, (im_src.shape[1],im_src.shape[0]))

            # cv2.imshow('Source Image', im_src)
            cv2.imshow("Warped Source Image", im_out)

            print(f'FPS: {1/(time.time()-last_time)}')
            last_time = time.time()
            # Press "q" to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break