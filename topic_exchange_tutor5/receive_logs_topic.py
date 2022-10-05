import pika
import sys


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()
channel.exchange_declare(exchange="topic_logs", exchange_type="topic")

# declare queue for duration of program
result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue
# extract binding keys from command line arguments. keys have format <facility>.<level>, representing
# the facility form which the log message came and its level of severity
binding_keys = sys.argv[1:]
if not binding_keys:
    sys.stderr.write(f"Usage: {sys.argv[0]} [binding_key]...\n")

# bind queue to receive only messages with binding keys given in command line arguments
for binding_key in binding_keys:
    channel.queue_bind(queue=queue_name,
                       exchange="topic_logs",
                       routing_key=binding_key)

print(" [*] Waiting for logs. To exit press CTRL + C")


def callback(ch, method, properties, body):
    print(f" [x] {method.routing_key}: {body}")


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()