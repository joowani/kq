from kafka import KafkaProducer

from kq import Queue


def add(a, b):
    return a + b


# Set up a Kafka producer.
producer = KafkaProducer(bootstrap_servers="127.0.0.1:9092")

# Set up a queue.
queue = Queue(topic="topic", producer=producer)

# Enqueue a function call.
job = queue.enqueue(add, 1, 2)
