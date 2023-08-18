# send_input.py
# send input to ETS2 via keyboard/mouse inputs
# note: controls.sii in game needs to be changed to:
#  config_lines[0]: "device keyboard `sys.keyboard`"
#  config_lines[1]: "device mouse `sys.mouse`"

import pydirectinput

def send_input(telemetry, steering, throttle):
    # use relative move to control steering
    # positive to steer right, negative to steer left
    """
    if throttle == 1:
        pydirectinput.keyUp("down", _pause=False)
        pydirectinput.keyDown("up", _pause=False)
    elif throttle == -1:
        pydirectinput.keyUp("up", _pause=False)
        pydirectinput.keyDown("down", _pause=False)
    else: # 0 throttle/brake, just coast
        pydirectinput.keyUp("down", _pause=False)
        pydirectinput.keyUp("up", _pause=False)
    """

    # TODO: fix asap!!
    curr_steering = telemetry["control_values"]["input"]["brake"]
    steering_error = curr_steering - steering
    # print(f'{curr_steering} > {steering} ?')
    steer(steering_error * 400)  # magic number calculated through magic
    # 100 pixels -> 0.2293 steer at 0.40 sens -> 436
    # 100 pixels -> 0.7524 steer at 1.50 sens -> 133
    """
    if curr_steering > steering:
        steer(10)
    else:
        steer(-10)
    """
    return


# TODO: change this to platform agnostic
# at the moment, moves the mouse to input steering
# positive = right, negative = left
def steer(movement):
    movement = round(movement)
    pydirectinput.move(movement, 0, _pause=False, relative=True)
