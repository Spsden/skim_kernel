import logging
import pika

from config.env import get_env
import json
from typing import Callable, Dict, Any


class QueueHandler:

    def __init__(self, channel_name: str) -> None:
        self.logger = logging.getLogger("MsgQueue")

        self.channel_name = channel_name

        queue_credentails = pika.PlainCredentials(
            username=get_env("MSG_QUEUE_USERNAME"),
            password=get_env("MSG_QUEUE_PASSWORD"),
        )

        connection_params = pika.ConnectionParameters(
            host=get_env("MSG_QUEUE"),
            port=get_env("MSG_QUEUE_PORT"),
            credentials=queue_credentails,
        )

        self.encode_type = "utf-8"

        try:
            self.connection = pika.BlockingConnection(connection_params)
            self.logger.info("Queue connection establisted.")
            self.channel = self.connection.channel()

        except Exception as e:
            self.logger.error(f"Queue init failed: {str(e)}")
            raise e

    def encode(self, msg: Dict[str, Any]) -> bytes:
        """to encode json / dict in sendable format"""
        return json.dumps(msg).encode(self.encode_type)

    def publisher(self, data: dict[str, Any]):
        try:
            # check for instance first
            if self.channel is None:
                self.logger.warning("Msg queue is not initialized")
                raise Exception("Msg queue is not initialized")

            # connect with correct channel
            self.channel.queue_declare(self.channel_name, durable=True)

            # to encode data
            encoded_data = self.encode(data)

            self.channel.basic_publish(
                exchange="",
                routing_key=self.channel_name,
                body=encoded_data,
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent
                ),
            )

            self.logger.info(f" Data added to queue: {self.channel_name}")

        except Exception as e:
            self.logger.error(f"Error publishing {str(e)}")

    def consume(self, call_back: Callable):
        try:

            def callback(ch, method, properties, body):
                # print(f"channel is {ch}")
                # print(f"method is {method}")
                # print(f" [x] Received {body}")
                call_back(body)

            self.channel.basic_consume(
                queue=self.channel_name, on_message_callback=callback
            )

            self.channel.start_consuming()

        except Exception as e:
            self.logger.error(f"Error consuming {str(e)}")

    def close_queue(self):
        self.connection.close()


if __name__ == "__main__":
    print("Queue in action")

    # queue = QueueHandler()

    # queue.publisher("hello_queue", {"name": "bhanu"})
