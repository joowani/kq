from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers="127.0.0.1:9092")

for _ in range(10000):
    producer.send("my_topic", b"message")
    # producer.flush()
