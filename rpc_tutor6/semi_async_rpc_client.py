import pika
import uuid

"""
Semi async, since we send the requests (in some order) then start consuming, then later the responses
come back in a different order, but we can't do anything after start_consuming(), so not overly useful.
However, another_async_client.py, which uses SelectConnection instead of BlockingConnection is not any more
useful than this. 

threaded_client.py actually does what I wanted.
"""

def on_response(ch, method, props, body):
    print(f"received response with correlation_id {props.correlation_id}: {body}")


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
    result = channel.queue_declare(queue="", exclusive=True)
    callback_queue = result.method.queue

    channel.basic_consume(
        queue=callback_queue,
        on_message_callback=on_response,
        auto_ack=True
    )

    print("A")
    call(38, channel, callback_queue)
    print("B")
    call(37, channel, callback_queue)
    print("C")
    call(10, channel, callback_queue)
    print("D")
    call(15, channel, callback_queue)
    print("E")

    channel.start_consuming()

    print("This never prints, fucking useless")


if __name__ == "__main__":
    main()
