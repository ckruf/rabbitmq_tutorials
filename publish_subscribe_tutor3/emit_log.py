import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()
# unlike in previous tutorials, here we are (explicitly) sending messages to an exchange,
# rather than a queue. An exchange receives messages from producers and pushes them to queues
# the exchange type determines what happens to received messages - are they appended to
# one particular queue? to many queues? 'fanout' broadcast all messages it receives to all queues it knows
channel.exchange_declare(exchange="logs", exchange_type="fanout")

message = ' '.join(sys.argv[1:]) or "info: Hello World!"
# publishing to exchange, rather than to queue
channel.basic_publish(exchange='logs', routing_key='', body=message)
print(" [x] Sent %r" % message)
connection.close()
