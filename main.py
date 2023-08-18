# main.py
# entry point for the program

import ctypes
from sys import platform
import time

import cv2
import mss
import numpy as np
from win32gui import (
    FindWindow,
    GetForegroundWindow,
    GetWindowRect,
)

from ets2_autopilot.imgproc import infer_polyline, CROP_X, CROP_Y, WIN_HEIGHT, WIN_WIDTH
from ets2_telemetry import get_telemetry
from ets2_autopilot.calc_input import CalcInput
from ets2_autopilot.send_input import send_input


def change_p(val):
    pid_controller.update_constants(Kp_steering=val / 100)


def change_i(val):
    pid_controller.update_constants(Ki_steering=val / 100)


def change_d(val):
    pid_controller.update_constants(Kd_steering=val / 100)


if __name__ == "__main__":
    print("Hello, world!")
    # DPI Scaling workaround from
    # https://stackoverflow.com/questions/44398075/can-dpi-scaling-be-enabled-disabled-programmatically-on-a-per-session-basis
    # This works for Win10/8 but not 7/Vista
    if platform == "win32":
        errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)

    window_handle = FindWindow(None, "Euro Truck Simulator 2")

    pid_controller = CalcInput(0.2, 0, 0, 0.1, 0, 0)
    cv2.namedWindow("PID tuning")
    cv2.createTrackbar("P", "PID tuning", round(pid_controller.Kp_steering*100), 100, change_p)
    cv2.createTrackbar("I", "PID tuning", round(pid_controller.Ki_steering*100), 100, change_i)
    cv2.createTrackbar("D", "PID tuning", round(pid_controller.Kd_steering*100), 100, change_d)

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
            # TODO: change to GetClientRect
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
            telemetry = get_telemetry()  # might have to dynamically update
            if len(centreline) > 0:
                dt = time.time() - last_time
                steering, throttle = pid_controller.calc_input(
                    telemetry, centreline, dt
                )
                # only send input if ETS2 is in focus
                # TODO: need to figure out some toggle to enable/disable input
                if GetForegroundWindow() == window_handle:
                    send_input(telemetry, steering, throttle)

            # print(f"FPS: {1/(time.time()-last_time)}")
            last_time = time.time()
            # Press "q" to quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break
    # end of loop
    print("Exiting...")
