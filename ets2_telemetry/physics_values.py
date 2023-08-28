import struct
from . import AbstractDataClass


class PhysicsValues(AbstractDataClass):
    """Get physics values that we might want to use"""

    linear_velocity = [0, 0, 0]
    linear_acceleration = [0, 0, 0]
    angular_velocity = [0, 0, 0]
    angular_acceleration = [0, 0, 0]

    def update(self, memory_map):
        linear_velocity_x = struct.unpack("f", memory_map[1868:1872])[0]
        linear_velocity_y = struct.unpack("f", memory_map[1872:1876])[0]
        linear_velocity_z = struct.unpack("f", memory_map[1876:1880])[0]

        self.linear_velocity = [linear_velocity_x, linear_velocity_y, linear_velocity_z]

        angular_velocity_x = struct.unpack("f", memory_map[1880:1884])[0]
        angular_velocity_y = struct.unpack("f", memory_map[1884:1888])[0]
        angular_velocity_z = struct.unpack("f", memory_map[1888:1892])[0]

        self.angular_velocity = [
            angular_velocity_x,
            angular_velocity_y,
            angular_velocity_z,
        ]

        linear_acceleration_x = struct.unpack("f", memory_map[1892:1896])[0]
        linear_acceleration_y = struct.unpack("f", memory_map[1896:1900])[0]
        linear_acceleration_z = struct.unpack("f", memory_map[1900:1904])[0]

        self.linear_acceleration = [
            linear_acceleration_x,
            linear_acceleration_y,
            linear_acceleration_z,
        ]

        angular_acceleration_x = struct.unpack("f", memory_map[1904:1908])[0]
        angular_acceleration_y = struct.unpack("f", memory_map[1908:1912])[0]
        angular_acceleration_z = struct.unpack("f", memory_map[1912:1916])[0]

        self.angular_acceleration = [
            angular_acceleration_x,
            angular_acceleration_y,
            angular_acceleration_z,
        ]
