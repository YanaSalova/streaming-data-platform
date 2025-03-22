import json
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from datetime import datetime

# Конфигурация Kafka
KAFKA_BROKER = 'kafka:9092'  # имя контейнера Kafka из docker-compose
TOPIC = 'user_events'

# Конфигурация Cassandra
CASSANDRA_CONTACT_POINTS = ['cassandra_db']  # имя контейнера Cassandra из docker-compose
KEYSPACE = 'mykeyspace'
TABLE = 'user_events'

# Функция для безопасного десериализатора
def safe_deserialize(x):
    try:
        # Если x пустой, вернём None
        if not x:
            return None
        return json.loads(x.decode('utf-8'))
    except json.JSONDecodeError as e:
        print("Ошибка при десериализации:", e, flush=True)
        return None

# Создание Kafka consumer с использованием безопасного десериализатора
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest',
    value_deserializer=safe_deserialize
)

# Подключение к Cassandra
cluster = Cluster(CASSANDRA_CONTACT_POINTS)
session = cluster.connect(KEYSPACE)

# Подготовка запроса для вставки
insert_query = SimpleStatement(
    f"INSERT INTO {TABLE} (country, event_time, id, name) VALUES (%s, %s, %s, %s)"
)

print("Kafka consumer запущен. Чтение сообщений...", flush=True)

for msg in consumer:
    # Если сообщение не удалось десериализовать или оно пустое, пропускаем его
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
