import pika
import uuid

"""
Not very useful in terms of async, since we can't do anything after starting the IO loop. No better
than semi_async_rpc_client. threaded_client.py actually does what I want to.
"""

channel = None
callback_queue = None


def on_connected(connection):
    connection.channel(on_open_callback=on_channel_open)


def on_channel_open(new_channel):
    global channel
    channel = new_channel
    channel.queue_declare(queue="", exclusive=True, callback=on_queue_declared)


def on_queue_declared(frame):
    global callback_queue
    callback_queue = frame.method.queue
    channel.basic_consume(callback_queue, on_response)

    print("A")
    call(38, channel, callback_queue)
    print("B")
    call(37, channel, callback_queue)
    print("C")
    call(10, channel, callback_queue)
    print("D")
    call(15, channel, callback_queue)
    print("E")


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


connection = pika.SelectConnection(
    pika.ConnectionParameters(host="localhost"),
    on_open_callback=on_connected
)


try:
    connection.ioloop.start()
    print("This never prints, so it's no more useful than BlockingConnection")
except KeyboardInterrupt:
    # Gracefully close the connection
    connection.close()
    # Loop until we're fully closed, will stop on its own
    connection.ioloop.start()



