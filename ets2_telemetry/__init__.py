from abc import ABC, abstractmethod
from multiprocessing.shared_memory import SharedMemory


class AbstractDataClass(ABC):
    """Outlines the data structure used to store the telemetry information"""

    @abstractmethod
    def update(self, memory_map):
        pass


class TelemetryReader:
    """This class allows you to hook into ETS2's telemetry stream and start reading from it"""

    # memory_location defined by
    # https://github.com/RenCloud/scs-sdk-plugin/blob/master/scs-telemetry/inc/scs-telemetry-common.hpp#L26
    memory_location = "Local\\SCSTelemetry"
    memory_map = None

    def __init__(self):
        """Initialise the telemetry reader, attempting the first hook"""
        self.hook_into_telemetry()

    def hook_into_telemetry(self):
        """Try to hook into the memory and start streaming information from it"""

        if self.memory_map is not None:
            # Have already hooked into the memory map. We do not do it again
            return

        try:
            self.memory_map = SharedMemory(self.memory_location)
        except FileNotFoundError:
            print(
                f"ETS2's telemetry located at {self.memory_location} is not to be found. Telemetry is not enabled"
            )

    def update_telemetry(self, data_class: AbstractDataClass):
        """Read the telemetry data"""
        if self.memory_map is None:
            print("Telemetry stream is not open. Can not update!")

        data_class.update(self.memory_map.buf)
