import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')
# we want each consumer to only receive logs which are currently being emitted,
# not old ones. Therefore, we declare a new queue on starup, which rabbit gives a random name to,
# by setting exclusive=True, the queue gets when consumer connection is closed
result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue

# tell exchange to send message to our newly created queue (this is called a 'binding')
channel.queue_bind(exchange="logs", queue=queue_name)


def callback(ch, method, properties, body):
    print(f" [x] {body}")


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print(" [*] Waiting for logs. To exit press CTRL + C")
channel.start_consuming()


