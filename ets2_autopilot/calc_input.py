import math


class CalcInput:
    def __init__(
        self,
        Kp_steering,
        Ki_steering,
        Kd_steering,
        Kp_throttle,
        Ki_throttle,
        Kd_throttle,
    ):
        # PID gains
        self.Kp_steering = Kp_steering
        self.Ki_steering = Ki_steering
        self.Kd_steering = Kd_steering

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

    def update_constants(
        self,
        Kp_steering=None,
        Ki_steering=None,
        Kd_steering=None,
        Kp_throttle=None,
        Ki_throttle=None,
        Kd_throttle=None,
    ):
        if Kp_steering is not None:
            self.Kp_steering = Kp_steering
        if Ki_steering is not None:
            self.Ki_steering = Ki_steering
        if Kd_steering is not None:
            self.Kd_steering = Kd_steering

        if Kp_throttle is not None:
            self.Kp_throttle = Kp_throttle
        if Ki_throttle is not None:
            self.Ki_throttle = Ki_throttle
        if Kd_throttle is not None:
            self.Kd_throttle = Kd_throttle

    def convert_to_seconds(self, timestamp_microseconds):
        return timestamp_microseconds / 1_000_000

    def filter_coordinates(self, centreline, threshold=0.1):
        return [coord for coord in centreline if coord[1] > threshold]

    def calculate_heading(self):
        # Implementation for calculating heading goes here
        pass

    def calculate_steering_error(self, centreline):
        steering_error = centreline[0][0]
        return steering_error

    def calculate_throttle_error(self, centreline, current_speed):
        desired_speed = self.calculate_desired_speed(centreline, current_speed)
        throttle_error = desired_speed - current_speed
        return throttle_error

    def calculate_desired_speed(self, centreline, current_position):
        # Implementation for calculating desired speed goes here
        return 0

    def calc_input(self, telemetry, centreline, dt):
        # Filter the coordinates
        filtered_centreline = self.filter_coordinates(centreline)

        # Calculate dt
        """
        dt = self.convert_to_seconds(
            telemetry["general_info"]["timestamp"] - self.prev_timestamp_steering
        )
        """
        # Steering PID
        steering_error = self.calculate_steering_error(filtered_centreline)
        self.steering_integral += steering_error * dt
        self.steering_integral = min(max(self.steering_integral, -1), 1)
        steering_derivative = (steering_error - self.prev_steering_error) / dt

        # Throttle PID
        # throttle_error = self.calculate_throttle_error(centreline, telemetry["truck"]["speed"])
        # placeholder
        throttle_error = self.calculate_throttle_error(filtered_centreline, 0)
        self.throttle_integral += throttle_error * dt
        throttle_derivative = (throttle_error - self.prev_throttle_error) / dt

        # Apply PID formula
        steering = (
            self.Kp_steering * steering_error
            + self.Ki_steering * self.steering_integral
            + self.Kd_steering * steering_derivative
        )
        throttle = (
            self.Kp_throttle * throttle_error
            + self.Ki_throttle * self.throttle_integral
            + self.Kd_throttle * throttle_derivative
        )

        # Clamp values
        steering = max(-1, min(1, steering))
        throttle = max(-1, min(1, throttle))

        # Update previous values
        self.prev_steering_error = steering_error
        self.prev_throttle_error = throttle_error
        self.prev_timestamp_steering = telemetry["general_info"]["timestamp"]
        self.prev_timestamp_throttle = telemetry["general_info"]["timestamp"]

        print(
            f"P: {round(self.Kp_steering * steering_error, 3):.3f}, I: {round(self.Ki_steering * self.steering_integral, 5):.5f}, D: {round(self.Kd_steering * steering_derivative, 3):.3f}"
        )
        return steering, throttle

    def is_ninety_degree_turn(
        self, centreline, severe_threshold=45, straight_threshold=15
    ):
        filtered_centreline = self.filter_coordinates(centreline)
        angles = []
        for i in range(1, len(centreline) - 1):
            x1, y1 = centreline[i - 1]
            x2, y2 = centreline[i]
            x3, y3 = centreline[i + 1]

            vec1 = (x2 - x1, y2 - y1)
            vec2 = (x3 - x2, y3 - y2)

            mag1 = math.sqrt(vec1[0] ** 2 + vec1[1] ** 2)
            mag2 = math.sqrt(vec2[0] ** 2 + vec2[1] ** 2)

            dot_product = vec1[0] * vec2[0] + vec1[1] * vec2[1]

            angle = math.degrees(math.acos(dot_product / (mag1 * mag2)))

            angles.append(angle)

        # Check for a severe angle variation and relatively straight paths before and after
        for i in range(1, len(angles) - 1):
            if angles[i] > severe_threshold:
                before_severe = all(angle < straight_threshold for angle in angles[:i])
                after_severe = all(
                    angle < straight_threshold for angle in angles[i + 1 :]
                )

                if before_severe and after_severe:
                    return True

        return False
