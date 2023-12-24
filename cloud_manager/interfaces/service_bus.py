"""
This interface is used to define the methods that each Service Bus class needs to implement.
"""
# Abtrsact methods are forced to be implemented
from abc import ABCMeta, abstractmethod


class ServiceBusInterface(metaclass=ABCMeta):
    """
    This interface is used to define the methods that each Service Bus class needs to implement.
    """

    @abstractmethod
    def publish(self, topic: str, message: str) -> None:
        """
        Publishes a message to the specified queue or topic.

        :param topic: The name of the topic to publish the message to.
        :param message: The message to be published.
        """
        pass

    @abstractmethod
    def consume(self, queue: str, callback: callable) -> None:
        """
        Consumes messages from the specified queue or topic and processes them using the provided callback function.

        :param queue: The name of the queue to consume messages from.
        :param callback: A callable that will be invoked for each message received. It should take one argument, which is the message.
        """
        pass
