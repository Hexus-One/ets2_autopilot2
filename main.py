# main.py
# entry point for the program

import ctypes
import time

import cv2
import mss
import numpy as np
from sys import platform
from win32gui import FindWindow, GetWindowRect # ignore squiggly, we have pywin32

import ets2_autopilot.imgproc as imgproc

if __name__ == '__main__':
    print('Hello, world!')
    # DPI Scaling workaround from
    # https://stackoverflow.com/questions/44398075/can-dpi-scaling-be-enabled-disabled-programmatically-on-a-per-session-basis
    # This works for Win10/8 but not 7/Vista
    if platform == 'win32':
        errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)

    WIN_WIDTH = imgproc.WIN_WIDTH
    WIN_HEIGHT = imgproc.WIN_HEIGHT
    CROP_X = imgproc.CROP_X
    CROP_Y = imgproc.CROP_Y
    window_handle = FindWindow(None, 'Euro Truck Simulator 2')

    with mss.mss() as sct:
        last_time = time.time()
        while True:
            # grab window position
            # assuming you're using Win10 + ETS2 in 1920x1080 window
            if window_handle == 0:
                print('ETS2 not found, waiting...')
                time.sleep(1)
                window_handle = FindWindow(None, 'Euro Truck Simulator 2')
                continue
            window_rect = GetWindowRect(window_handle)
            ets2_window = {'top': window_rect[1] + CROP_Y,
                        'left': window_rect[0] + CROP_X + 10, # no clue why +10
                        'width': WIN_WIDTH - CROP_X,
                        'height': WIN_HEIGHT - CROP_Y
                        }
            im_src = np.array(sct.grab(ets2_window))
            # get centreline from image
            centreline = imgproc.infer_polyline(im_src)

            # TODO: convert thinned mask to polyline
            # TODO: get telemetry data from game
            # TODO: determine ideal steering angle from polyline + telemetry
            # TODO: send input to game

            cv2.imshow('Source Image', im_src)

            print(f'FPS: {1/(time.time()-last_time)}')
            last_time = time.time()
            # Press "q" to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
    # end of loop
    print('Exiting...')