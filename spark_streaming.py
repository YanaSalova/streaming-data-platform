from pyspark.sql import SparkSession
from pyspark.sql.functions import to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

spark = SparkSession.builder.appName("FileToKafka").getOrCreate()


schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("country", StringType(), True)
])


df = (spark.readStream
    .format("json")
    .option("multiline", "true")
    .schema(schema)
    .load("/app/data")
)

kafka_df = df.select(to_json(struct("*")).alias("value"))

query = (kafka_df.writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("topic", "user_events")
    .option("checkpointLocation", "/app/data/checkpoints")
    .start()
)

query.awaitTermination()
