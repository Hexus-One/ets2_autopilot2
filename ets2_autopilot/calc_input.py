# calc_input.py
# from telemetry and centreline, calculate what inputs to send

# telemetry avaiable is here: https://github.com/RenCloud/scs-sdk-plugin#telemetry-fields-and-the-c-object
# centreline scale is 1 unit -> 25cm
#  (x, y) -> (0, 0) is centre of the cab
#  +x is left, -x is right, +y is forwards and -y is backwards
def calculate_heading():
    # Implementation for calculating heading goes here
    pass

def calculateSteeringError(centreline, current_position):
    # Implementation for calculating steering error goes here
    pass

def calculateThrottleError(centreline, current_speed):
    # Implementation for calculating throttle error goes here
    pass

def calc_input(telemetry, centreline):
    # PID gains (you will need to tune these values)
    Kp_steering = 0
    Ki_steering = 0
    Kd_steering = 0

    Kp_throttle = 0
    Ki_throttle = 0
    Kd_throttle = 0

    # Initialize PID errors for steering
    steering_error = 0
    steering_integral = 0
    steering_derivative = 0
    prev_steering_error = 0

    # Initialize PID errors for throttle
    throttle_error = 0
    throttle_integral = 0
    throttle_derivative = 0
    prev_throttle_error = 0

    # Calculate steering error
    steering_error = calculateSteeringError(centreline, telemetry["truck"]["heading"])
    steering_integral += steering_error
    steering_derivative = steering_error - prev_steering_error

    # Calculate throttle error
    throttle_error = calculateThrottleError(centreline, telemetry["truck"]["speed"])
    throttle_integral += throttle_error
    throttle_derivative = throttle_error - prev_throttle_error

    # Apply PID formula for steering
    steering = Kp_steering * steering_error + Ki_steering * steering_integral + Kd_steering * steering_derivative

    # Apply PID formula for throttle
    throttle = Kp_throttle * throttle_error + Ki_throttle * throttle_integral + Kd_throttle * throttle_derivative

    # Clamp values
    steering = max(-1, min(1, steering))
    throttle = max(-1, min(1, throttle))

    return steering, throttle
