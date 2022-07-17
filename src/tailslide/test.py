import asyncio
import threading
import time
import nats
from nats.errors import ConnectionClosedError, TimeoutError
messages = []


async def message_handler(messageObj):
    message = messageObj.data.decode()
    messages.append(message)
    print(message)


async def main():
    await fetchOngoingMessages()


async def fetchOngoingMessages():
    nats_connection = await nats.connect('localhost')
    jet_stream = nats_connection.jetstream()
    app_id = "9"
    config = nats.js.api.ConsumerConfig(
        deliver_policy=nats.js.api.DeliverPolicy.NEW)
    subscribed_stream = await jet_stream.subscribe(stream="flags", subject=app_id, config=config, cb=message_handler)

    while True:
        try:
            message_response = await subscribed_stream.next_msg()
            print(message_response)
            # message = message_response.data.decode()
            # self.callback(message)
        except ConnectionClosedError:
            print('disconnected from nats')
            break
        except TimeoutError as e:
            print("Error:", e)
        except AttributeError:
            pass

if __name__ == '__main__':
    asyncio.run(main())
