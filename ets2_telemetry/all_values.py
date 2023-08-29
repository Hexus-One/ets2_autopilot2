import struct
from . import AbstractDataClass
from .general_info import GeneralInfo
from .physics_values import PhysicsValues
from .sdk_values import SDKInfo
from .truck_values import TruckValues
from .user_inputs import UserInputs


class AllValues(AbstractDataClass):
    """Contains everything that I am bothered to add"""

    general_info = GeneralInfo()
    physics_values = PhysicsValues()
    sdk_values = SDKInfo()
    truck_values = TruckValues()
    user_inputs = UserInputs()

    def update(self, memory_map):
        self.general_info.update(memory_map)
        self.physics_values.update(memory_map)
        self.sdk_values.update(memory_map)
        self.truck_values.update(memory_map)
        self.user_inputs.update(memory_map)
