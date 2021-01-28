from kafka import KafkaConsumer

consumer = KafkaConsumer("my_topic")

print("Starting consumer...")
for msg in consumer:
    print(msg)
