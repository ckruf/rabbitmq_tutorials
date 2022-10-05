import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
# create durable queue called task_queue - it will survive a RabbitMQ restart
# however messages also need to be marked as durable so they persist between restarts
channel.queue_declare(queue="task_queue", durable=True)
message = " ".join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(exchange="",
                      routing_key="task_queue",
                      body=message,
                      properties=pika.BasicProperties(
                          delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                      ))
# PERSISTENT_DELIVERY_MODE above marks messages as durable - they won't be lost on restart

print(f" [x] sent {message}")
connection.close()

