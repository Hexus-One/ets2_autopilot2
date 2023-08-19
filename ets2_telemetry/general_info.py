import struct
from . import AbstractDataClass


class GeneralInfo(AbstractDataClass):
    """Information about the game such if the SDK is active or game is paused"""

    sdk_active = False
    game_paused = False
    timestamp = 0
    simulated_timestamp = 0
    render_timestamp = 0
    multiplayer_time = 0

    def update(self, memory_map):
        self.sdk_active = bool(struct.unpack("I", memory_map[0:4])[0])
        self.paused = bool(struct.unpack("I", memory_map[4:8])[0])

        self.timestamp = struct.unpack("Q", memory_map[8:16])[0]
        self.simulated_timestamp = struct.unpack("Q", memory_map[16:24])[0]
        self.render_timestamp = struct.unpack("Q", memory_map[24:32])[0]
        self.multiplayer_time = struct.unpack("Q", memory_map[32:40])[0]
