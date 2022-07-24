import asyncio
import json

import nats
from nats.errors import ConnectionClosedError, TimeoutError

messages = []


class NatsClient():
    def __init__(self, server='nats://localhost:4222', subject='', callback=None, sdk_key=''):
        self.nats_connection = None
        self.jet_stream_manager = None
        self.jet_stream = None
        self.subscribed_stream = None
        self.server = server
        self.nats_config = {"servers": server, "token": sdk_key}
        self.subject = str(subject)
        self.callback = callback or (lambda _: _)
        self.future = asyncio.Future()

    async def initialize_flags(self):
        await self.connect()
        future = await self.fetch_latest_messages()
        asyncio.ensure_future(self.fetch_ongoing_event_messages())
        return future

    async def connect(self):
        self.nats_connection = await nats.connect(**self.nats_config)
        self.jet_stream_manager = nats.js.JetStreamManager(conn=self.server)
        self.jet_stream = self.nats_connection.jetstream()

    async def fetch_latest_messages(self):
        config = nats.js.api.ConsumerConfig(
            deliver_policy=nats.js.api.DeliverPolicy.LAST,
            )
        subscribed_stream = await self.jet_stream.subscribe(stream="flags", subject=self.subject, config=config)
        try:
            message_response = await subscribed_stream.next_msg(timeout=None)
            message = message_response.data.decode()
            json_data = json.loads(message)
            if not self.future.done():
                self.future.set_result(json_data)
            self.callback(json_data)
            await subscribed_stream.unsubscribe()
        except ConnectionClosedError as e:
            print('disconnected from nats', e)
        return self.future

    async def fetch_ongoing_event_messages(self):
        await self.latest_flags_ready()
        config = nats.js.api.ConsumerConfig(
            deliver_policy=nats.js.api.DeliverPolicy.NEW,
            )
        self.subscribed_stream = await self.jet_stream.subscribe(stream="flags", subject=self.subject, config=config)

        while self.nats_connection.is_connected:
            try:
                message_response = await self.subscribed_stream.next_msg(timeout=None)
                message = message_response.data.decode()
                self.callback(message)
            except ConnectionClosedError as e:
                print('disconnected from nats', e)
                break

    def latest_flags_ready(self):
        return self.future

    async def disconnect(self):
        self.nats_connection.close()

    # async def __del__(self):
    #     print('closing nats')
    #     await self.nats_connection.close()
