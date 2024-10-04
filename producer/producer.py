import asyncio
import json
import pandas as pd
import os
import random
from dotenv import load_dotenv
import tweepy as tw
import jsonlines
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient

load_dotenv("../.env")

# LOADING EVENT HUB CONNECTION DATA
EVENT_HUB_CONNECTION_STR = os.getenv("EVENT_HUB_CONNECTION_STR")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")

# LOADING TWITTER TOKEN
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET")

TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# MESSAGES BACKUP
TWEETS_FILE_PATH = "../data/messages_backup.json"
DUMMY_DATA = pd.read_csv("../data/elonmusk_tweets.csv")


def save_message_backup(message_json):
    with jsonlines.open(TWEETS_FILE_PATH, 'a') as json_writer:
        json_writer.write(message_json)


def generate_original_tweets(max_results: int = 10):
    tw_client = tw.Client(
        bearer_token=TWITTER_BEARER_TOKEN
    )

    query = '#elonmusk -is:retweet lang:en'
    tweets = tw_client.search_recent_tweets(
        query=query,
        tweet_fields=['id_str', 'created_at', 'text'],
        max_results=max_results
    )
    result = []

    for message in tweets.data:
        message_json = message._json
        save_message_backup(message_json)
        result.append(json.dumps(message_json))

    return result


def generate_dummy_tweets(max_results: int = 10):
    start_row = random.randint(0, len(DUMMY_DATA) - max_results - 1)
    messages_df = DUMMY_DATA.iloc[start_row: start_row + max_results]

    result = []
    for index, row in messages_df.iterrows():
        result.append(json.dumps(row.to_json()))
    return result


async def run():
    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR,
        eventhub_name=EVENT_HUB_NAME
    )
    async with producer:
        event_data_batch = await producer.create_batch()

        tweets = generate_dummy_tweets(max_results=10)
        for message in tweets:
            event_data_batch.add(EventData(message))

        await producer.send_batch(event_data_batch)


if __name__ == "__main__":
    while True:
        asyncio.run(run())
