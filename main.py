# main.py
# entry point for the program

import ctypes
from datetime import datetime
from os.path import join
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

from ets2_imgproc import infer_polyline, CROP_X, CROP_Y, WIN_HEIGHT, WIN_WIDTH
from ets2_telemetry import TelemetryReader
from ets2_telemetry.general_info import GeneralInfo
import ets2_autopilot.calc_input as calc_input
from ets2_autopilot.send_input import send_input

OUTPUT = r"tests\data"


def main():
    print("Hello, world!")
    # DPI Scaling workaround from
    # https://stackoverflow.com/questions/44398075/can-dpi-scaling-be-enabled-disabled-programmatically-on-a-per-session-basis
    # This works for Win10/8 but not 7/Vista
    if platform == "win32":
        errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)

    global im_src
    telemetry = TelemetryReader()
    general_info = GeneralInfo()
    window_handle = FindWindow(None, "Euro Truck Simulator 2")

    with mss.mss() as sct:
        last_time = time.perf_counter_ns()
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
            telemetry.update_telemetry(general_info)
            if len(centreline) > 0:
                dt = time.perf_counter_ns() - last_time
                steering = calc_input.CalcInput.pure_pursuit_control_car(
                    centreline, 10, 3.85289538  # magic wheelbase
                )
                # only send input if ETS2 is in focus and unpaused
                # TODO: need to figure out some toggle to enable/disable input
                if (
                    GetForegroundWindow() == window_handle
                    and general_info.paused == False
                ):
                    send_input(telemetry, steering, 0)
                    pass
            elapsed = (time.perf_counter_ns() - last_time) / 1_000_000_000
            fps = 1 / elapsed
            print(f"FPS: {round(fps, 2):06.2f}" + "-" * round(fps / 10))
            last_time = time.perf_counter_ns()
            # Press "q" to quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break
    # end of loop
    print("Exiting...")


if __name__ == "__main__":
    try:
        main()
    except Exception as inst:  # set a breakpoint here as well
        cv2.waitKey(1)
        name = datetime.now().strftime("crash_%Y-%m-%d_%H-%M-%S.png")
        name = join(OUTPUT, name)
        cv2.imwrite(name, im_src)
        print("Program crashed!")
