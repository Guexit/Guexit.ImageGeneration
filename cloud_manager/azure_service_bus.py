import time
import traceback
from typing import Callable, Optional

from azure.servicebus import AutoLockRenewer, ServiceBusClient, ServiceBusMessage
from azure.servicebus.exceptions import OperationTimeoutError, ServiceBusError

from cloud_manager.custom_logging import set_logger
from cloud_manager.interfaces.service_bus import ServiceBusInterface

logger = set_logger("Azure Service Bus")


class AzureServiceBus(ServiceBusInterface):
    def __init__(
        self, connection_string: str, max_lock_renewal_duration: int = 300
    ) -> None:
        logger.info("Initializing Azure Service Bus")
        try:
            self.client = ServiceBusClient.from_connection_string(
                connection_string,
                max_lock_renewal_duration=max_lock_renewal_duration,
            )
        except ValueError as e:
            logger.error(f"Invalid connection string: {e}")
            raise

        self.auto_lock_renewer = AutoLockRenewer()

    def publish(self, topic: str, message: str) -> None:
        try:
            with self.client.get_queue_sender(topic) as sender:
                msg = ServiceBusMessage(message)
                sender.send_messages(msg)
                logger.info(f"Published message to '{topic}': {message}")
        except Exception as e:
            logger.error(f"Error publishing message to '{topic}': {e}")

    def consume(self, queue: str, callback: Callable[[str], None]) -> None:
        try:
            with self.client.get_queue_receiver(
                queue,
                auto_lock_renew=True,
                auto_lock_renewer=self.auto_lock_renewer,
            ) as receiver:
                for msg in receiver:
                    callback(str(msg))
                    receiver.complete_message(msg)
                    logger.info(f"Consumed message from '{queue}': {msg}")
        except Exception as e:
            logger.error(f"Error consuming messages from '{queue}': {e}")

    def consume_indefinitely(
        self,
        queue: str,
        callback: Callable[[str], None],
        max_number_messages: Optional[int] = None,
        max_retries: Optional[int] = 3,
        base_retry_delay: Optional[int] = 5,  # seconds
    ) -> None:
        retry_count = 0
        processed_messages = 0
        while retry_count < max_retries:
            try:
                with self.client.get_queue_receiver(
                    queue,
                    max_wait_time=30,
                    auto_lock_renew=True,
                    auto_lock_renewer=self.auto_lock_renewer,
                ) as receiver:
                    for msg in receiver:
                        if isinstance(msg, Exception):
                            raise msg  # Re-raise the exception to be caught by outer except blocks
                        try:
                            callback(str(msg))
                            receiver.complete_message(msg)
                            logger.info(f"Consumed message from '{queue}': {msg}")
                            retry_count = (
                                0  # reset retry count on successful consumption
                            )

                            processed_messages += 1
                            if (
                                max_number_messages is not None
                                and processed_messages >= max_number_messages
                            ):
                                return
                        except Exception as e:
                            logger.error(f"Error while processing message: {e}")
                            traceback.print_exc()
                            break  # Exit the loop to prevent the error from happening again
            except OperationTimeoutError:
                logger.warning(
                    f"No messages received from '{queue}' in last 30 seconds."
                )
            except ServiceBusError as e:
                logger.error(f"ServiceBusError encountered: {e}")
                traceback.print_exc()
                retry_count += 1
                time.sleep(base_retry_delay * (2**retry_count))  # exponential backoff
            except Exception as e:
                logger.error(f"Unexpected error encountered: {e}")
                traceback.print_exc()
                retry_count += 1
                time.sleep(base_retry_delay * (2**retry_count))  # exponential backoff
