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
        await self.fetchLatestMessages()
        await self.fetchOngoingMessages()

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

    async def fetchOngoingMessages(self):
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


async def main():

    async def disconnected_cb():
        print("Got disconnected...")

    async def reconnected_cb():
        print("Got reconnected...")

    nc = await nats.connect("127.0.0.1",
                            reconnected_cb=reconnected_cb,
                            disconnected_cb=disconnected_cb,
                            max_reconnect_attempts=-1
                            )

    js = nc.jetstream()

    config = nats.js.api.ConsumerConfig(
        deliver_policy=nats.js.api.DeliverPolicy.NEW)

    # consumer_info = await js.add_consumer(
    #     "flags",
    #     durable_name="dur",
    #     deliver_policy=nats.js.api.DeliverPolicy.ALL,
    #     deliver_subject="10"
    # )
    sub = await js.subscribe(stream="flags", subject="9", config=config)

    message = await sub.next_msg()
    print(message)
    print("Listening for requests")
    for i in range(1, 1000000):
        try:
            message = await sub.next_msg()
            print(message.data.decode())
        except Exception as e:
            print("Error:", e)


def logger(message):
    print(message)
    messages.append(message)


async def log_messages(natClient):
    await natClient.latestFlagsReady()
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
        task1 = asyncio.create_task(natsClient.fetchFlags())
        task2 = asyncio.create_task(log_messages(natsClient))
        await task1
        await task2
        print('hello')
        print(messages)

    except Exception as e:
        print(e)

if __name__ == '__main__':
    asyncio.run(main())
