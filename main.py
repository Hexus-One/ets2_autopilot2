# main.py
# entry point for the program

import ctypes
from sys import platform
import time

import cv2
import mss
import numpy as np
from win32gui import FindWindow, GetWindowRect  # ignore squiggly, we have pywin32

from ets2_autopilot.imgproc import infer_polyline, CROP_X, CROP_Y, WIN_HEIGHT, WIN_WIDTH
from ets2_autopilot.telemetry import get_telemetry
from ets2_autopilot.calc_input import calc_input
from ets2_autopilot.send_input import send_input

if __name__ == "__main__":
    print("Hello, world!")
    # DPI Scaling workaround from
    # https://stackoverflow.com/questions/44398075/can-dpi-scaling-be-enabled-disabled-programmatically-on-a-per-session-basis
    # This works for Win10/8 but not 7/Vista
    if platform == "win32":
        errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)

    window_handle = FindWindow(None, "Euro Truck Simulator 2")

    with mss.mss() as sct:
        last_time = time.time()
        while True:
            # grab window position
            # assuming you're using Win10 + ETS2 in 1920x1080 window
            if window_handle == 0:
                print("ETS2 not found, waiting...")
                time.sleep(1)
                window_handle = FindWindow(None, "Euro Truck Simulator 2")
                continue
            window_rect = GetWindowRect(window_handle)
            ets2_window = {
                "top": window_rect[1] + CROP_Y,
                "left": window_rect[0] + CROP_X + 10,  # no clue why +10
                "width": WIN_WIDTH - CROP_X,
                "height": WIN_HEIGHT - CROP_Y,
            }
            # sct.grab is synced to refresh rate,
            # limiting the loop to 60fps or 30fps (if it misses a frame)
            im_src = np.array(sct.grab(ets2_window))

            # magic happens here
            centreline, _ = infer_polyline(im_src)
            telemetry = get_telemetry()
            steering, throttle = calc_input(telemetry, centreline)
            send_input(steering, throttle)

            print(f"FPS: {1/(time.time()-last_time)}")
            last_time = time.time()
            # Press "q" to quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break
    # end of loop
    print("Exiting...")
