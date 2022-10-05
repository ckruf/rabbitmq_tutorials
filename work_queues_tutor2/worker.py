import pika
import sys
import os
import time


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    # create durable queue called task_queue - it will survive a RabbitMQ restart
    # however messages also need to be marked as durable so they persist between restarts
    channel.queue_declare(queue="task_queue", durable=True)

    def callback(ch, method, properties, body):
        print(f" [x] received {body.decode()}")
        time.sleep(body.count(b'.'))
        print(" [x] Done")
        # sending acknowledgement to RabbitMQ that the message has been processed and
        # can be deleted. If program fails before sending ack, Rabbit will re-queue the message
        # and deliver it to a different consumer
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # prefetch_count=1 tells RabbitMQ not to give more than one message to a worker
    # at a given time
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="task_queue",
                          on_message_callback=callback)

    print(" [*] Waiting for messages. To exit press CTRL + C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
