import asyncio
import threading
import time
import nats
from nats.errors import ConnectionClosedError, TimeoutError
messages = []


class NatsClient():
    def __init__(self, server='localhost', app_id=None, callback=None, sdk_key=''):
        self.nats_connection = None
        self.jet_stream_manager = None
        self.jet_stream = None
        self.subscribed_stream = None
        self.server = server
        self.nats_config = {"servers": server, "token": sdk_key}
        self.app_id = str(app_id)
        self.callback = callback or (lambda _: _)
        self.future = asyncio.Future()

    async def fetchFlags(self):
        await self.connect()
        future = await self.fetchLatestMessages()
        asyncio.ensure_future(self.fetchOngoingMessages())
        return future
        # await self.fetchOngoingMessages()

    async def connect(self):
        print('connecting')
        self.nats_connection = await nats.connect(self.server)
        self.jet_stream_manager = nats.js.JetStreamManager(conn=self.server)
        self.jet_stream = self.nats_connection.jetstream()

    async def fetchLatestMessages(self):
        psub = await self.jet_stream.pull_subscribe(self.app_id, "psub")
        message = await psub.fetch(1)
        if not self.future.done():
            self.future.set_result(message)
        self.callback(message)
        return self.future

    async def fetchOngoingMessages(self):
        await self.latestFlagsReady()
        config = nats.js.api.ConsumerConfig(
            deliver_policy=nats.js.api.DeliverPolicy.NEW)
        self.subscribed_stream = await self.jet_stream.subscribe(stream="flags", subject=self.app_id, config=config)

        while self.nats_connection.is_connected:
            try:
                message_response = await self.subscribed_stream.next_msg()
                message = message_response.data.decode()
                self.callback(message)

                # self.callback(message)
            except ConnectionClosedError:
                print('disconnected from nats')
                break
            except TimeoutError as e:
                print("Error:", e)
            except AttributeError:
                pass

    def latestFlagsReady(self):
        return self.future

    async def disconnect(self):
        self.nats_connection.close()

    # async def __del__(self):
    #     print('closing nats')
    #     await self.nats_connection.close()


def logger(message):
    print(message)
    messages.append(message)


async def log_messages():
    # await natClient.latestFlagsReady()
    while True:
        print(messages)
        await asyncio.sleep(3)


async def print_numbers():
    for i in range(10):
        print(i)
        await asyncio.sleep(1)


async def main():
    natsClient = NatsClient(app_id=9, callback=logger)
    try:
        # task1 = asyncio.create_task(natsClient.fetchFlags())
        # task2 = asyncio.create_task(log_messages(natsClient))
        # await task1
        # await task2
        await natsClient.fetchFlags()
        # await log_messages()
        print('hello')
        print(messages)

    except Exception as e:
        print(e)

if __name__ == '__main__':
    asyncio.run(main())
