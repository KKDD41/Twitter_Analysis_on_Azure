#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from pyspark.sql.functions import col, cast
from pyspark.sql.types import *

# Event Hub details
EH_CONN_STR = dbutils.secrets.get(scope="eventhub-scope", key="eventhub-conn-str")
EH_NAMESPACE = "eventhub-namespace-twitter-analysis"        # my-event-hubs-namespace
EH_KAFKA_TOPIC = "eventhub-twitter-analysis"                # my-event-hub
EH_BOOTSTRAP_SERVERS = f"{EH_NAMESPACE}.servicebus.windows.net:9093"
EH_SASL_WRITE = f'kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required username="$ConnectionString" password="{EH_CONN_STR}";'

# Azure SQL Database Details
SQL_DB_URL = "jdbc:sqlserver://sqlserver-twitter-analysis.database.windows.net:1433;database=db-twitter-analysis"
SQL_DB_USERNAME = dbutils.secrets.get(scope="sqldb-scope", key="sqldb-username")
SQL_DB_PASSWORD = dbutils.secrets.get(scope="sqldb-scope", key="sqldb-password")


# standard configuration options
topic_name = EH_KAFKA_TOPIC
eh_namespace_name = EH_NAMESPACE
eh_sasl = EH_SASL_WRITE
bootstrap_servers = EH_BOOTSTRAP_SERVERS
kafka_options = {
    "kafka.bootstrap.servers": bootstrap_servers,
    "kafka.sasl.mechanism": "PLAIN",
    "kafka.security.protocol": "SASL_SSL",
    "kafka.request.timeout.ms": "60000",
    "kafka.session.timeout.ms": "30000",
    "startingOffsets": "earliest",
    "kafka.sasl.jaas.config": eh_sasl,
    "subscribe": topic_name,
}


# In[ ]:


get_ipython().run_line_magic('sql', '')

CREATE TABLE IF NOT EXISTS tweets
(
    Key BINARY,
    Value BINARY,
    Topic STRING,
    Partition INT,
    Offset LONG,
    Timestamp TIMESTAMP,
    TimestampType INT,
    Value_text STRING
) using DELTA


# In[ ]:


kafka_df = (
    spark.readStream.format("kafka")
    .options(**kafka_options)
    .load()
    .withColumn("value_text", col("value").cast("string"))
)


# In[ ]:


kafka_df.writeStream.outputMode("append").option(
    "checkpointLocation", "/tmp/delta/events/_checkpoints/"
).toTable("tweets")


# In[ ]:


get_ipython().run_line_magic('sql', '')
SELECT
  value_text
FROM
  hive_metastore.default.tweets;


# In[ ]:


from pyspark.sql.functions import (
    col,
    current_timestamp,
    from_json,
    cast,
    lit,
    from_unixtime,
    to_timestamp,
    sum,
    avg,
    when,
    count,
    round,
    max,
    explode,
    regexp_replace,
    left,
    right,
    expr,
    dayofweek,
    udf,
    length,
    to_date
)
from pyspark.sql.types import (
    StructField,
    StructType,
    IntegerType,
    StringType,
    DoubleType,
    LongType,
    TimestampType,
)

tweets_schema = StructType(
    fields=[
        StructField("id_str", StringType(), True),
        StructField("created_at", StringType(), True),
        StructField("text", StringType(), True),
    ]
)


# In[ ]:


tweets_df = (
    spark.sql("SELECT * FROM hive_metastore.default.tweets")
    .drop("key", "value", "partition", "offset", "Timestamp", "Timestamptype")
    .withColumn("JSON", from_json(regexp_replace(expr("substring(value_text, 2, length(value_text) - 2)"), r'\\', ''), tweets_schema))
    .withColumn("id", col("JSON.id_str"))
    .withColumn("text", col("JSON.text"))
    .withColumn("created_at", col("JSON.created_at"))
    .drop("JSON", "value_text", "Topic")
    .withColumn("week_day", dayofweek(col("created_at")))
    .withColumn("text_length", length(col("text")))
    .dropDuplicates()
)


# In[ ]:


display(tweets_df)


# In[ ]:


import re

def extract_mentions(text):
    if not text:
        return None
    return re.findall(r'@(\w+)', text)

extract_mentions_udf = udf(extract_mentions, ArrayType(StringType()))

mentions_df = tweets_df.withColumn("mentions", extract_mentions_udf(col("text"))) \
    .selectExpr("id as tweet_id", "explode(mentions) as username")

total_mentions_df = mentions_df.groupBy("username").count()


# In[ ]:


display(mentions_df)


# In[ ]:


display(total_mentions_df)


# In[ ]:


tweets_count_by_date_df = tweets_df.withColumn("date", to_date(tweets_df.created_at)).groupBy("date").agg(count("*").alias("count"), sum("text_length").alias("total_tweets_length"))


# In[ ]:


display(tweets_count_by_date_df)


# In[ ]:


try:
    (
        tweets_df.coalesce(1)
        .write.format("jdbc")
        .option("url", SQL_DB_URL)
        .option("dbtable", "dbo.tweets")
        .option("user", SQL_DB_USERNAME)
        .option("password", SQL_DB_PASSWORD)
        .mode("append")
        .save()
    )

    (
        mentions_df.coalesce(1)
        .write.format("jdbc")
        .option("url", SQL_DB_URL)
        .option("dbtable", "dbo.mentions")
        .option("user", SQL_DB_USERNAME)
        .option("password", SQL_DB_PASSWORD)
        .mode("append")
        .save()
    )

    (
        total_mentions_df.coalesce(1)
        .write.format("jdbc")
        .option("url", SQL_DB_URL)
        .option("dbtable", "dbo.total_mentions")
        .option("user", SQL_DB_USERNAME)
        .option("password", SQL_DB_PASSWORD)
        .mode("append")
        .save()
    )

    (
        tweets_count_by_date_df.coalesce(1)
        .write.format("jdbc")
        .option("url", SQL_DB_URL)
        .option("dbtable", "dbo.tweets_by_date")
        .option("user", SQL_DB_USERNAME)
        .option("password", SQL_DB_PASSWORD)
        .mode("append")
        .save()
    )

    print("Successfully write data into target SQL database")
except Exception as error:
    print("An exception occurred:", error)

