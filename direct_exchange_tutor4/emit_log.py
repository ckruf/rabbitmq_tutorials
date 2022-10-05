import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()
# a direct exchange - allows us to send messages to specific queues, rather than sending all messages
# to all queues as 'fanout' does
channel.exchange_declare(exchange="direct_logs", exchange_type="direct")

severity = sys.argv[1] if len(sys.argv) > 1 else "info"
message = ' '.join(sys.argv[2:]) or "Hello World!"

# the message now has a routing_key, which will determine what queues it will be sent to
channel.basic_publish(exchange='direct_logs', routing_key=severity, body=message)
print(" [x] Sent %r" % message)
connection.close()
