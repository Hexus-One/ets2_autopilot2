import ctypes
import time

import cv2
import mss
import numpy as np
from win32gui import FindWindow, GetWindowRect # ignore squiggly, we have pywin32

if __name__ == '__main__':
    print("Hello, world!")
    # DPI Scaling workaround from
    # https://stackoverflow.com/questions/44398075/can-dpi-scaling-be-enabled-disabled-programmatically-on-a-per-session-basis
    # This works for Win10/8 but not 7/Vista
    errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)

    # hardcoded GPS colours, remember its BGRA not RGBA
    GREEN_MIN = (6, 229, 17, 255)
    GREEN_MAX = (28, 251, 97, 255)
    RED_MIN = (11, 11, 194, 255)
    RED_MAX = (42, 42, 207, 255)
    KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

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
    h, status = cv2.findHomography(PTS_SRC, PTS_DST)
    window_handle = FindWindow(None, "Euro Truck Simulator 2")

    with mss.mss() as sct:
        last_time = time.time()
        while True:
            # grab window position
            # assuming you're using Win10 + ETS2 in 1920x1080 window
            window_rect = GetWindowRect(window_handle)
            ets2_window = {"top": window_rect[1]+CROP_Y,
                        "left": window_rect[0]+10+CROP_X, # no clue why
                        "width": 1921-CROP_X,
                        "height": 1120-CROP_Y
                        }
            im_src = np.array(sct.grab(ets2_window))
            green_mask = cv2.inRange(im_src, GREEN_MIN, GREEN_MAX)
            red_mask = cv2.inRange(im_src, RED_MIN, RED_MAX)
            comb_mask = cv2.bitwise_or(green_mask, red_mask)
            comb_mask = cv2.morphologyEx(comb_mask, cv2.MORPH_CLOSE, KERNEL)
            comb_mask_inv = cv2.bitwise_not(comb_mask)
            im_tmp3 = cv2.bitwise_and(im_src, im_src, mask=comb_mask_inv)
            im_out = cv2.warpPerspective(im_src, h, (1921, 1120), flags=cv2.INTER_NEAREST)
            # thinned = cv2.ximgproc.thinning(comb_mask)
            # thin_warp = cv2.warpPerspective(thinned, h, (1921, 1120), flags=cv2.INTER_NEAREST)
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
            """
            # draw on og HUD
            cv2.drawContours(comb_mask, contours, -1, (0, 0, 255), 1)

            # warp contours for transformed perspective
            warped_contours = []
            for contour in contours:
                # discard degenerate contours that probably don't represent road
                if contour.size < 5:
                    continue
                contourf = contour.astype(np.float32)
                warped_cont = cv2.perspectiveTransform(contourf, h)
                warped_contours.append(warped_cont.astype(int))
            cv2.drawContours(im_out, warped_contours, -1, (255, 255, 255), 1)

            cv2.imshow('Source Image', im_src)
            cv2.imshow('Mask', comb_mask)
            # cv2.imshow('Thinned', thinned)
            cv2.imshow('Warped Source Image', im_out)

            print(f'FPS: {1/(time.time()-last_time)}')
            last_time = time.time()
            # Press "q" to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
    # end of loop