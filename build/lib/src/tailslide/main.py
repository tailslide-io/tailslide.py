import asyncio
import json
import threading
import time

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

    async def fetchFlags(self):
        await self.connect()
        future = await self.fetchLatestMessages()
        asyncio.ensure_future(self.fetchOngoingMessages())
        return future

    async def connect(self):
        self.nats_connection = await nats.connect(**self.nats_config)
        self.jet_stream_manager = nats.js.JetStreamManager(conn=self.server)
        self.jet_stream = self.nats_connection.jetstream()

    async def fetchLatestMessages(self):
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
            self.callback(message)
        except ConnectionClosedError:
            print('disconnected from nats')
        except TimeoutError as e:
            print("Error:", e)
        except AttributeError:
            pass
        await subscribed_stream.unsubscribe()
        return self.future

    async def fetchOngoingMessages(self):
        await self.latestFlagsReady()
        config = nats.js.api.ConsumerConfig(
            deliver_policy=nats.js.api.DeliverPolicy.NEW,
            )
        self.subscribed_stream = await self.jet_stream.subscribe(stream="flags", subject=self.subject, config=config)

        while self.nats_connection.is_connected:
            try:
                message_response = await self.subscribed_stream.next_msg(timeout=None)
                message = message_response.data.decode()
                self.callback(message)
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




async def main():
    natsClient = NatsClient(subject='test', callback=logger, sdk_key="myToken")
    try:
        # task1 = asyncio.create_task(natsClient.fetchFlags())
        # task2 = asyncio.create_task(log_messages(natsClient))
        # await task1
        # await task2
        await natsClient.fetchFlags()
        print('hello')
        while True:
            await asyncio.sleep(2)
            print(messages)

    except Exception as e:
        print(e)

if __name__ == '__main__':
    asyncio.run(main())
