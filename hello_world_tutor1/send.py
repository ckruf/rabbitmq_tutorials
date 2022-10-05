import pika

# connect to RabbitMQ running on localhost:5672
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
# create queue called hello
channel.queue_declare(queue="hello")

# messages are never sent directly to a queue, they must go through an exchange first.
# here, we are using the default exchange, identified by the empty string.

channel.basic_publish(exchange="",
                      routing_key="hello",
                      body='Hello world')
print(" [x] sent 'Hello world'")
connection.close()
