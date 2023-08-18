import struct


def get_input_values(telemetry_memory_map):
    """Get user's input values"""
    return {
        "steer": struct.unpack("f", telemetry_memory_map[776:780])[0],
        "throttle": struct.unpack("f", telemetry_memory_map[784:788])[0],
        "brake": struct.unpack("f", telemetry_memory_map[792:796])[0],
        "clutch": struct.unpack("f", telemetry_memory_map[796:800])[0],
    }


def get_game_values(telemetry_memory_map):
    """Get the game's control values"""
    return {
        "steer": struct.unpack("f", telemetry_memory_map[800:804])[0],
        "throttle": struct.unpack("f", telemetry_memory_map[804:808])[0],
        "brake": struct.unpack("f", telemetry_memory_map[808:812])[0],
        "clutch": struct.unpack("f", telemetry_memory_map[812:816])[0],
    }


def get_control_values(telemetry_memory_map):
    """Get the values need to control your truck"""
    return {
        "input": get_input_values(telemetry_memory_map),
        "game": get_game_values(telemetry_memory_map),
    }
