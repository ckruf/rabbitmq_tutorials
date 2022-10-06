# RabbitMQ
## Introduction
- RabbitMQ is a message broker - it accepts and forwards messages
- The overall messaging model in RabbitMQ is the following: 

<img src="./notes_assets/python-three-overall.png">

Messages are sent by a producer (P) to an exchange (X). The exchange then pushes the messages into queues. The messages are then received from the queue(s) by consumers (C<sub>1</sub> and C<sub>2</sub>).

## RabbitMQ tutorials
Can be found [here](https://www.rabbitmq.com/getstarted.html).

Pre-requisites: 
- have RabbitMQ installed and running, most easily done using the docker image:
 `docker run -it --rm --name mytestrabbit -p 5672:5672 -p 15672:15672 rabbitmq:3.10-management`
- Install pika (assuming Python) `pip install pika`

## Code examples/lessons learned/whatever

### Connecting to RabbitMQ

The first step in any application making use of RabbitMQ is to create a TCP connection to our RabbitMQ. There are two main ways to make a connection with pika - the `BlockingConnection` class and the `SelectConnection` class. `BlockingConnection` is easier to use, because it is more conforming to Python's synchronous style. As its name suggests, it blocks execution when waiting for results of operations which are actually asynchronous. On the other hand `SelectConnection` makes use of callbacks, its approach is more similar to (old) Javascript. After making a connection, we use the `Channel` class as the primary communication method for interacting with RabbitMQ. 

```
# first two steps in any Rabbit app, whether producer or consumer

connection = pika.BlockingConnection(
    pika.ConnectionParameters()
)
channel = connection.channel()

# most basic sending of message, mostly for demonstration comparison to SelectConnection

channel.basic_publish(exchange="", routing_key="hello", body="Hello world")
connection.close()
```

```
# Step 3
def on_open(connection):
    connection.channel(on_open_callback=on_channel_open)

# Step 4
def on_channel_open(channel):
    channel.basic_publish(exchange="", routing_key="hello", body="Hello world")
    connection.close()


# Step #1: Connect to RabbitMQ
connection = pika.SelectConnection(
    pika.ConnectionParameters()
)

try:
    # Step #2 - Block on the IOLoop
    connection.ioloop.start()
except KeyboardInterrupt:
    connection.close()
    # Start the IOLoop again so Pika can communicate, it will stop on its own when the connection is closed
    connection.ioloop.start)()
```
### Sending messages

Producers send messages to exchanges, which can then forward them to queues. One way to send messages is the `basic_publish()` method (of the `Channel` class - like most methods). Sending a message typically looks like this:

```
# prerequisites - connection, channel, exchange

message = "Hello, world"

channel.basic_publish(
    exchange="my_exchange",
    routing_key="example_key",
    body=message
)
```

### Exchanges - types, routing

Exchanges receive messages from producers and forward them to queues. We must declare a binding between a queue and an exchange for the messages to be forwarded. 

<img src="./notes_assets/bindings.png">

There are several types of exchanges, which differ in their routing. Routing determines to which queues the messages will be forwarded (while a binding between a queue and an exchange is necessary, for most exchanges it is not sufficient). These are the types of exchanges, (matched to RabbitMQ tutorials):

1. **fanout exchange** (tutorial 3)

The fanout exchange sends messages to all queues to which it has a binding.

2. **direct exchange** (tutorial 4)

A direct exchange forwards messages to queues whose binding key (the routing key of their binding) exactly matches the routing key of the message. This allows these kind of setups:

<img src="./notes_assets/direct-exchange.png">

In this setup, any messages with a routing key of "orange" would be sent to Q1 and any messages with a routing key of "black" or "green" would be sent to Q2. Note that bindings are done per routing key, so for Q2 we would have to create two bindings to the exchange. 

It is also possible to bind multiple queues with the same binding key, like so:

<img src="./notes_assets/direct-exchange-multiple.png">

3. topic exchange (tutorial 5)

Topic exchanges are quite similar to direct exchanges, in that they also forward messages to queues based on a routing key. However, the routing key for a topic exchange must have a specific format - a list of words, separated by dots. Additionally, there are two special cases for binding keys. `*` can substitute for exactly one word and `#` can substitute for zero or more words. Example:

<img src="./notes_assets/python-five.png">

In the example above, a message with a routing_key of `quick.orange.rabbit` would go to both Q1 and Q2. `lazy.brown.rabbit` would be sent to Q2 only, and only once, despite matching both bindings.  

4. header exchange

In a header exchange, the messages are forwarded to queues based on headers, rather than routing keys. This is similar to a topic exchange, but rather than being restricted to a string routing key, we match based on headers, which have a format of `Dict[str, any]`. Additionally, when we create the queue binding, we can specify whether the values of all headers need to match, or if matching any headers is sufficient (using the `x-match` arguemnt). Code example is included below, because the header exchange is not used in any of the RabbitMQ tutorials.
```
# sending message
channel.basic_publish(
    exchange="my_header_exchange",
    routing_key="",  # routing key is ignored by header exchange
    body=message,
    properties=pika.BasicProperties(headers={"name": "chris"})
)

# queue binding
bind_args = {
    "x-match": "any",
    "name": "chris",
    "importance": "high"
}
channel.queue_bind("my_queue", "my_header_exchange", arguments=bind_args)
```

5. default exchange (tutorial 1)

If we don't specify an exchange, then the default exchange is used. Any queue that is declared is automatically bound to the default exchange, and will receive messages from it if the routing_key of the message matches the name of the queue.

### Multiple queue consumers (competing consumers pattern, tutorial 2)

Queues can have more than one consumer. A typical use case is a *Work queue*, where we send messages representing time-consuming tasks to workers (the consumers). The tasks can then be distributed among them. This is particularly useful in web application, if we have a time consuming task which can not be done immediately during a short HTTP request window. We send the task to workers to be done later. 

<img src="./notes_assets/python-two.png">

Note, however, that a particular message from the queue can only be consumed by one consumer. It is not possible for both consumer to consume the same message.

#### Fair dispatching

By default, RabbitMQ uses round-robin dispatching, meaning that each message is sent to the next consumer, in sequence. In case of two workers, one would get all the even messages, and one would get all the odd messages. On average, every consumer will get the same number of messages.

However, this might not always be the best way to dispatch messages. It could happen that all the even tasks happen to be very hard and the odd ones happen to be easy. In this case one of the workers would be constantly busy, while the other would not be doing anything most of the time. We can use `channel.basic_qos(prefetch_count=1)` to ensure that a worker is only given one message at a time. This would lead to a more fair distribution of tasks. 

### Message acknowledgements

When the messages we are sending represent tasks which could take some time to complete, it could happen that the worker receives the task, starts working on it and then dies part way through. In this case, the task would not be completed, and the message would be lost. This is where message acknowledgements come in.
```
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body.decode())
    time.sleep(random.randint(1, 10))  # simulate task which takes some time
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)
```

In this example, the consumer sends an ack(nowledgement) to RabbitMQ, notifying it that it has fully processed the task, and that RabbitMQ can delete the message. If the worker dies part way through completing the task, the message is not akcnowledged, so RabbitMQ will requeue it and deliver it to another consumer.

### Message durability

By default, RabbitMQ will forget all our messages if it crashes. We can make message durable (surviving restarts) by using the appropriate setting for queues and messages.

```
channel.queue_declare(queue='task_queue', durable=True)

channel.basic_publish(exchange='',
                      routing_key="task_queue",
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode = pika.spec.PERSISTENT_DELIVERY_MODE
                      ))
```

This does not guarantee 100% that all messages won't be lost, since there is some time between receiving the message and writing it to the disk.

### RPCs