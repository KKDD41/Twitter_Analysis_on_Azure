import asyncio
import os
import json
from dotenv import load_dotenv
import tweepy as tw
import jsonlines
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient

load_dotenv("../.env")

# LOADING EVENT HUB CONNECTION DATA
EVENT_HUB_CONNECTION_STR = os.getenv("EVENT_HUB_CONNECTION_STR")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")
print(EVENT_HUB_CONNECTION_STR)
print(EVENT_HUB_NAME)

# LOADING TWITTER TOKEN
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# MESSAGES BACKUP
TWEETS_FILE_PATH = "../data/messages_backup.json"


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
        tweet_fields=['context_annotations', 'created_at'],
        max_results=max_results
    )
    result = []

    for message in tweets.data:
        message_json = message._json
        save_message_backup(message_json)
        result.append(message_json)

    return result


def generate_dummy_tweets(max_results: int = 10):
    tweet_structure = {}

    with open("response_example.json", "r") as f:
        tweet_structure = json.loads(f.read())

    result = []
    for i in range(max_results):
        tweet_structure[
            "text"] = f"Congratulations! You received {i}-th dummy tweet from dummy producers, and did not spend a cent on X API!"
        result.append(json.dumps(tweet_structure))

    return result


async def run():
    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR,
        eventhub_name=EVENT_HUB_NAME
    )
    async with producer:
        event_data_batch = await producer.create_batch()

        tweets = generate_dummy_tweets(max_results=100)
        for message in tweets:
            event_data_batch.add(EventData(message))

        await producer.send_batch(event_data_batch)

asyncio.run(run())
