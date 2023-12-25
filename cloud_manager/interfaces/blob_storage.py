"""
This interface is used to define the methods that each Cloud class needs to implement.
"""
# Abtrsact methods are forced to be implemented
from abc import ABCMeta, abstractmethod


class BlobStorageInterface(metaclass=ABCMeta):
    """
    This interface is used to define the methods that each Cloud class needs to implement.
    """

    @abstractmethod
    def push_objects(self, objects: list):
        """
        This method is used to push objects to the cloud.
        """
        pass
