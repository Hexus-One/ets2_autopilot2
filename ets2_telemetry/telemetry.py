import struct


def get_general_info(telemetry_memory_map):
    """Get information about the game such if the SDK is active or game is paused"""
    return {
        "sdk_active": struct.unpack("I", telemetry_memory_map[0:4])[0],
        "paused": struct.unpack("I", telemetry_memory_map[4:8])[0],
        "timestamp": struct.unpack("Q", telemetry_memory_map[8:16])[0],
        "simulated_timestamp": struct.unpack("Q", telemetry_memory_map[16:24])[0],
        "render_timestamp": struct.unpack("Q", telemetry_memory_map[24:32])[0],
        "multiplayer_timeoffset": struct.unpack("Q", telemetry_memory_map[32:40]),
    }
