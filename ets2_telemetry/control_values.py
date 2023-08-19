import struct
from . import AbstractDataClass


class UserInputs(AbstractDataClass):
    steer = 0.0
    throttle = 0.0
    brake = 0.0
    clutch = 0.0

    def update(self, memory_map):
        self.steer = struct.unpack("f", memory_map[956:960])[0]
        self.throttle = struct.unpack("f", memory_map[960:964])[0]
        self.brake = struct.unpack("f", memory_map[968:972])[0]
        self.clutch = struct.unpack("f", memory_map[972:976])[0]
