import json

import grpc
from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
import logging
import os
from model.cloud_events import CloudEvent

quote_aggregate_table = os.getenv('QUOTE_AGGREGATE_TABLE', '')

app = FastAPI()

logging.basicConfig(level=logging.INFO)

async def main():
    async with DaprClient() as client:
    
        subscription = await client.subscribe_with_handler(
                pubsub_name='pubsub', topic='quotes', handler_fn=loan_quotes, dead_letter_topic='undeliverable')


async def loan_quotes(event: CloudEvent) -> TopicEventResponse:
    
    with DaprClient() as d:
        try:

            logging.info(f'Received event: %s:' % {event.data["quote_aggregate"]})

            quote_aggregate = json.loads(event.data['quote_aggregate'])
            
            # save aggregate data
            d.save_state(store_name=quote_aggregate_table,
                         key=str(quote_aggregate['request_id']),
                         value=json.dumps(quote_aggregate),
                         state_metadata={"contentType": "application/json"})


        except grpc.RpcError as err:
            logging.info(f"Error={err}")
            raise HTTPException(status_code=500, detail=err.details())


if __name__ == '__main__':
    asyncio.run(main())