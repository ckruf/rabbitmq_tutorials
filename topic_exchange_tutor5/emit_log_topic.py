import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()
channel.exchange_declare(exchange="topic_logs", exchange_type="topic")

# routing key has format <facility>.<level>, representing the facility from which the log message
# came and its level of severity
routing_key = sys.argv[1] if len(sys.argv) > 2 else "anonymous.info"
message = " ".join(sys.argv[2:]) or "Hello world"
channel.basic_publish(exchange="topic_logs",
                      routing_key=routing_key,
                      body=message)
print(f" [x] Sent {routing_key} {message}")
connection.close()
