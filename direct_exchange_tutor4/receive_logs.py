import sys

import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue

severities = sys.argv[1:]
if not severities:
    sys.stderr.write(f"Usage: {sys.argv[0]} [info] [warning] [error]\n")

# bind queue to receive logs of appropriate level from direct_logs exchange
for severity in severities:
    channel.queue_bind(
        exchange="direct_logs", queue=queue_name, routing_key=severity
    )


def callback(ch, method, properties, body):
    print(f" [x] {method.routing_key}: {body}")


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print(" [*] Waiting for logs. To exit press CTRL + C")
channel.start_consuming()


