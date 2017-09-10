from abc import ABC, abstractmethod

class Info(ABC):

    @abstractmethod
    def get_device_info(self):
        pass


# Modules must implement this, to ensure they have the required responses expected for the security policy
# TODO: Gateway needs to verify this method is implemented in the module.
