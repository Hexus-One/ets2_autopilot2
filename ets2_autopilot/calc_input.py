# calc_input.py
# from telemetry and centreline, calculate what inputs to send

# telemetry avaiable is here: https://github.com/RenCloud/scs-sdk-plugin#telemetry-fields-and-the-c-object
# centreline scale is 1 unit -> 25cm
#  (x, y) -> (0, 0) is centre of the cab
#  +x is left, -x is right, +y is forwards and -y is backwards
import math

class CalcInput:
    def __init__(self, Kp_steering, Ki_steering, Kd_steering, Kp_throttle, Ki_throttle, Kd_throttle):
        # PID gains for steering
        self.Kp_steering = Kp_steering
        self.Ki_steering = Ki_steering
        self.Kd_steering = Kd_steering

        # PID gains for throttle
        self.Kp_throttle = Kp_throttle
        self.Ki_throttle = Ki_throttle
        self.Kd_throttle = Kd_throttle

        # Previous errors
        self.prev_steering_error = 0
        self.prev_throttle_error = 0

        # Previous timestamp
        self.prev_timestamp_steering = 0
        self.prev_timestamp_throttle = 0

        # Steering and Throttle Integral
        self.steering_integral = 0
        self.throttle_integral = 0

    # ... (Rest of the class implementation)


    def calculate_heading(self):
        # Implementation for calculating heading goes here
        pass

    def calculate_steering_error(self, centreline, heading):
        steering_error = centreline[0][0]
        return steering_error

    def calculate_throttle_error(self, centreline, current_speed):
        desired_speed = self.calculate_desired_speed(centreline, current_speed)
        throttle_error = desired_speed - current_speed
        return throttle_error

    def calculate_desired_speed(self, centreline, current_position):
        # Implementation for calculating desired speed goes here
        pass

    def calc_input(self, telemetry, centreline):
        # ... (Same code as before)

        return steering, throttle

    def is_ninety_degree_turn(self, centreline, severe_threshold=45, straight_threshold=15):
        # ... (Same code as before)

        return False
