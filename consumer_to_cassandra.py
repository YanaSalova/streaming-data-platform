import json
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from datetime import datetime

KAFKA_BROKER = 'kafka:9092'  
TOPIC = 'user_events'


CASSANDRA_CONTACT_POINTS = ['cassandra_db'] 
KEYSPACE = 'mykeyspace'
TABLE = 'user_events'


def safe_deserialize(x):
    try:
        if not x:
            return None
        return json.loads(x.decode('utf-8'))
    except json.JSONDecodeError as e:
        print("Ошибка при десериализации:", e, flush=True)
        return None


consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest',
    value_deserializer=safe_deserialize
)

cluster = Cluster(CASSANDRA_CONTACT_POINTS)
session = cluster.connect(KEYSPACE)


insert_query = SimpleStatement(
    f"INSERT INTO {TABLE} (country, event_time, id, name) VALUES (%s, %s, %s, %s)"
)

print("Kafka consumer запущен. Чтение сообщений...", flush=True)

for msg in consumer:
    if msg.value is None:
        continue

    print(f"Получено сообщение: {msg.value}", flush=True)
    event_time = datetime.now()

    try:
        session.execute(insert_query, (
            msg.value.get('country'),
            event_time,
            msg.value.get('id'),
            msg.value.get('name')
        ))
        print("Данные записаны в Cassandra", flush=True)
    except Exception as e:
        print("Ошибка при вставке в Cassandra:", e, flush=True)