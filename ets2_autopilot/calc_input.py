# calc_input.py
# from telemetry and centreline, calculate what inputs to send

# telemetry avaiable is here: https://github.com/RenCloud/scs-sdk-plugin#telemetry-fields-and-the-c-object
# centreline scale is 1 unit -> 25cm
#  (x, y) -> (0, 0) is centre of the cab
#  +x is left, -x is right, +y is forwards and -y is backwards
def calc_input(telemetry, centreline):
    steering = 0 # some number between -1, 1 (1 is left, -1 is right)
    throttle = 0 # some integer -1, 0, 1 (-1 is brake, 1 is throttle)

    # magic here

    return steering, throttle