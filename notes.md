# RabbitMQ
## Introduction
- RabbitMQ is a message broker - it accepts and forwards messages
- The overall messaging model in RabbitMQ is the following: 

<img src="./notes_assets/python-three-overall.png">

Messages are sent by a producer (P) to an exchange (X). The exchange then pushes the messages into queues. The messages are then received from the queue(s) by consumers (C<sub>1</sub> and C<sub>2</sub>).

## RabbitMQ tutorials
Can be found [here](https://www.rabbitmq.com/getstarted.html).

Pre-requisites: 
- have RabbitMQ installed and running, most easily done using the docker image
`docker run -it --rm --name mytestrabbit -p 5672:5672 -p 15672:15672 rabbitmq:3.10-management`
- Install pika (assuming Python) `pip install pika`

### Code examples/lessons learned/whatever

The first step in any application making use of RabbitMQ is to create a TCP connection to our RabbitMQ. There are two main ways to make a connection with pika - the `BlockingConnection` class and the `SelectConnection` class. `BlockingConnection` is easier to use, because it is more conforming to Python's synchronous style. As its name suggests, it blocks execution when waiting for results of operations which are actually asynchronous. On the other hand `SelectConnection` make use of callbacks, its approach is more similar to (old) Javascript. After making a connection, we use the `Channel` class as the primary communication method for interacting with RabbitMQ. 

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