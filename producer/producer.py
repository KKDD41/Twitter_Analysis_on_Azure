import asyncio
import os
import json
from dotenv import load_dotenv

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient

load_dotenv("../.env")

# LOADING EVENT HUB CONNECTION DATA
EVENT_HUB_CONNECTION_STR = os.getenv("EVENT_HUB_CONNECTION_STR")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")


# https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-python-get-started-send?tabs=connection-string%2Croles-azure-portal

async def run():
    # Create a producer client to send messages to the event hub.
    # Specify a connection string to your event hubs namespace and
    # the event hub name.
    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR, eventhub_name=EVENT_HUB_NAME
    )
    async with producer:
        # Create a batch.
        event_data_batch = await producer.create_batch()

        # Add events to the batch.
        # Batch size default: 100.
        for i in range(50):
            message = {
                "id": i,
                "message": f"{i} times hello",
                "sender": "senior data engineer"
            }
            event_data_batch.add(EventData(json.dumps(message)))

        # Send the batch of events to the event hub.
        await producer.send_batch(event_data_batch)


asyncio.run(run())
