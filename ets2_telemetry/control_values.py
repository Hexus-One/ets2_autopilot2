import struct


def get_input_values(telemetry_memory_map):
    """Get user's input values"""
    return {
        "steer": struct.unpack("f", telemetry_memory_map[956:960])[0],
        "throttle": struct.unpack("f", telemetry_memory_map[960:964])[0],
        "brake": struct.unpack("f", telemetry_memory_map[968:972])[0],
        "clutch": struct.unpack("f", telemetry_memory_map[972:976])[0],
    }


def get_game_values(telemetry_memory_map):
    """Get the game's control values"""
    return {
        "steer": struct.unpack("f", telemetry_memory_map[976:980])[0],
        "throttle": struct.unpack("f", telemetry_memory_map[980:984])[0],
        "brake": struct.unpack("f", telemetry_memory_map[984:988])[0],
        "clutch": struct.unpack("f", telemetry_memory_map[988:992])[0],
    }


def get_control_values(telemetry_memory_map):
    """Get the values need to control your truck"""
    return {
        "input": get_input_values(telemetry_memory_map),
        "game": get_game_values(telemetry_memory_map),
    }
