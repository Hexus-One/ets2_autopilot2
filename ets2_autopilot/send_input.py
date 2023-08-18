# send_input.py
# send input to ETS2 via keyboard/mouse inputs
# note: controls.sii in game needs to be changed to:
#  config_lines[0]: "device keyboard `sys.keyboard`"
#  config_lines[1]: "device mouse `sys.mouse`"

import pydirectinput


def send_input(telemetry, steering, throttle):
    # use relative move to control steering
    # positive to steer right, negative to steer left
    steer(10)
    """
    if telemetry["InputValues"]["Steering"] > steering:
        steer(5)
    else:
        steer(-5)
    """
    return


# TODO: change this to platform agnostic
def steer(movement):
    pydirectinput.move(movement, 0, _pause=False, relative=True)
