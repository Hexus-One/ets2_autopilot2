# calc_input.py
# from telemetry and centreline, calculate what inputs to send

# telemetry avaiable is here: https://github.com/RenCloud/scs-sdk-plugin#telemetry-fields-and-the-c-object
# centreline scale is 1 unit -> 25cm
#  (x, y) -> (0, 0) is centre of the cab
#  +x is left, -x is right, +y is forwards and -y is backwards
def calculate_heading():
    # Implementation for calculating heading goes here
    pass

def calculateSteeringError(centreline):
    # Get the x-coordinate of the first point in the centreline
    steering_error = centreline[0][0]

    # You can scale or modify this error based on your specific requirements
    # E.g., you might want to normalize it by the length of the track or apply a specific scaling factor

    return steering_error

def calculateThrottleError(centreline, current_speed):
    # Calculate the desired speed based on the centreline and current position
    desired_speed = calculateDesiredSpeed(centreline, current_position)

    # The throttle error is the difference between the desired speed and the current speed
    throttle_error = desired_speed - current_speed

    return throttle_error

def calc_input(telemetry, centreline):
    # PID gains
    Kp_steering = 0
    Ki_steering = 0
    Kd_steering = 0

    Kp_throttle = 0
    Ki_throttle = 0
    Kd_throttle = 0

    # Previous errors
    prev_steering_error = 0
    prev_throttle_error = 0

    # Previous timestamp
    prev_timestamp_steering = telemetry["timestamp"]
    prev_timestamp_throttle = telemetry["timestamp"]

    # Calculate dt
    dt_steering = telemetry["timestamp"] - prev_timestamp_steering
    dt_throttle = telemetry["timestamp"] - prev_timestamp_throttle

    # Steering PID
    steering_error = calculateSteeringError(centreline, telemetry["truck"]["heading"])
    steering_integral = steering_error * dt_steering
    steering_derivative = (steering_error - prev_steering_error) / dt_steering

    # Throttle PID
    throttle_error = calculateThrottleError(centreline, telemetry["truck"]["speed"])
    throttle_integral = throttle_error * dt_throttle
    throttle_derivative = (throttle_error - prev_throttle_error) / dt_throttle

    # Apply PID formula
    steering = Kp_steering * steering_error + Ki_steering * steering_integral + Kd_steering * steering_derivative
    throttle = Kp_throttle * throttle_error + Ki_throttle * throttle_integral + Kd_throttle * throttle_derivative

    # Clamp values
    steering = max(-1, min(1, steering))
    throttle = max(-1, min(1, throttle))

    # Update previous values
    prev_steering_error = steering_error
    prev_throttle_error = throttle_error
    prev_timestamp_steering = telemetry["timestamp"]
    prev_timestamp_throttle = telemetry["timestamp"]

    return steering, throttle
