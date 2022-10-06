import pika
import uuid
import threading
import time

"""
This actually does what I've been trying to do - lets me run other code while waiting for messages.
"""


def start_consumer(callback_queue):
    def on_response(ch, method, props, body):
        print(f"received response with correlation_id {props.correlation_id}: {body}")

    print("start_consumer running")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )

    channel = connection.channel()

    channel.basic_consume(
        queue=callback_queue,
        on_message_callback=on_response,
        auto_ack=True
    )

    channel.start_consuming()


def call(n, channel, callback_queue):
    corr_id = str(uuid.uuid4())
    print(f"Sending request for fib({n}) with correlation_id {corr_id}")
    channel.basic_publish(
        exchange="",
        routing_key="rpc_queue",
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=corr_id
        ),
        body=str(n)
    )


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )

    channel = connection.channel()

    # create queue to which the server should send the response/result of our RPC
    result = channel.queue_declare(queue="")
    callback_queue = result.method.queue

    consumer_thread = threading.Thread(target=start_consumer, args=(callback_queue,))
    consumer_thread.start()

    print("0")
    call(10, channel, callback_queue)
    print("A")
    call(38, channel, callback_queue)
    print("B")
    call(37, channel, callback_queue)
    print("C")
    call(10, channel, callback_queue)
    print("D")
    call(15, channel, callback_queue)
    print("E")

    print("Just chilling over here")

    print("Gonna have a nap")
    time.sleep(3)
    print("That felt good")
    print("I can do whatever I want")

    call(35, channel, callback_queue)

    call(36, channel, callback_queue)

    print("Just sent two more requests like it's nobody's business")


if __name__ == "__main__":
    main()
