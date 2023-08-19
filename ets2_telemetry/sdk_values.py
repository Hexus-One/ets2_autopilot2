import struct
from . import AbstractDataClass


class SDKInfo(AbstractDataClass):
    """Information about the game such if the SDK is active or game is paused"""

    plugin_version = 0
    game_version_major = 0
    game_version_minor = 0
    # The SDK is compatible with different Euro Truck Simulators. The game_type values are
    # as follow,
    # 0 => Unknown
    # 1 => EuroTruck Simulator 2 (ETS2)
    # 2 => EuroTruck Simulator 1 (ETS)
    # The reason why index 1 is given to ETS2 is because the SDK was made only for ETS2
    # and later backported
    game_type = 0
    telemetry_version_major = 0
    telemetry_version_minor = 0

    def update(self, memory_map):
        self.plugin_version = struct.unpack("I", memory_map[40:44])[0]
        self.game_version_major = struct.unpack("I", memory_map[44:48])[0]
        self.game_version_minor = struct.unpack("I", memory_map[48:52])[0]
        self.game_type = struct.unpack("I", memory_map[52:56])[0]
        self.telemetry_version_major = struct.unpack("I", memory_map[56:60])[0]
        self.telemetry_version_minor = struct.unpack("I", memory_map[60:64])[0]
