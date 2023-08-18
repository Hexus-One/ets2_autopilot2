from mmap import mmap

from general_info import get_general_info
from control_values import get_control_values

# Defined by https://github.com/RenCloud/scs-sdk-plugin/blob/master/scs-telemetry/inc/scs-telemetry-common.hpp#L26
memory_map_length = 1024
shared_memory_location = "Local\\SCSTelemetry"
telemetry_memory_map = mmap(0, memory_map_length, shared_memory_location)

general_info = get_general_info(telemetry_memory_map)
control_values = get_control_values(telemetry_memory_map)
