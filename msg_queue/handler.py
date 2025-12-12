
import logging
import pika

from config.env import get_env

class QueueHandler:
    
    def __init__(self) -> None:
        self.logger = logging.getLogger("MsgQueue")

        queue_credentails = pika.PlainCredentials(
            username=get_env("MSG_QUEUE_USERNAME"), 
            password=get_env("MSG_QUEUE_PASSWORD")
        )

        connection_params = pika.ConnectionParameters(
            host=get_env("MSG_QUEUE"),
            port=get_env("MSG_QUEUE_PORT"),
            credentials=queue_credentails,
        )
        
        try:
            self.connection = pika.BlockingConnection(connection_params)
            self.logger.info("Queue connection establisted.")
            self.channel = self.connection.channel()


        except Exception as e:
            self.logger.error(f"Queue init failed: {str(e)}")
            raise e

    
    def publisher(self, channel_name: str):
        try:
            # check for instance first

            if self.channel is None:
                self.logger.warning("Msg queue is not initialized")
                raise Exception("Msg queue is not initialized")
            
            # connect with correct channel
            self.channel.queue_declare(channel_name, durable=True)

            self.channel.basic_publish(
                exchange='',
                routing_key=channel_name, 
                body='Hello World! 11111',
                properties=pika.BasicProperties(
                    delivery_mode = pika.DeliveryMode.Persistent
                )
            )
            
            self.logger.info(
                f"Message sent to exchange for channel name: {channel_name}"
            )

            self.connection.close()


        except Exception as e:
            self.logger.error(f"Error publishing {str(e)}")

    
    def consume(self, channel_name: str):
        try:
            def callback(ch, method, properties, body):
                print(f" [x] Received {body}")

            self.channel.basic_consume(queue=channel_name, on_message_callback=callback)

            print(' [*] Waiting for messages. To exit press CTRL+C')
            self.channel.start_consuming()

        except Exception as e:
            self.logger.error(f"Error consuming {str(e)}")


if __name__ == "__main__":
    print("Queue in action")

    queue = QueueHandler()

    queue.publisher("hello_queue")
    