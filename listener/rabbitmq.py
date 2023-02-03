import aio_pika
import asyncio
from .frappe import create_card_request, create_cert_request
from .postgres import get_connect, is_card_ignored, is_cert_ignored

async def process_event(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    c = await get_connect()
    print(c)

    async with message.process():
        match message.headers["Event"]:
            case "CardConnect":
                await log_event(message)
                if not await is_ignored(message):
                    pass
                    await create_card_request(message)
            case "CardDisconnect":
                await log_event(message)
            case "CertFound":
                await log_event(message)
                if not await is_ignored(message):
                    pass
                    await create_cert_request(message)
            case _:
                pass


async def new_connection(loop) -> aio_pika.Connection:
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/",
        loop=loop
    )
    return connection


async def new_channel(connection: aio_pika.Connection) -> aio_pika.Channel:
    channel = await connection.channel()
    # Maximum message count which will be processing at the same time.
    await channel.set_qos(prefetch_count=100)
    return channel


async def new_queue(queue_name: str, channel: aio_pika.Channel) -> aio_pika.Queue:
    queue = await channel.declare_queue(queue_name)
    return queue


async def setup_rabbitmq(loop):
    connection = await new_connection(loop)
    channel = await new_channel(connection)
    ping_queue = await new_queue("ping_event", channel)
    event_queue = await new_queue("agent_event", channel)
    await ping_queue.consume(process_event)
    await event_queue.consume(process_event)
    
    try:
        await asyncio.Future()
    finally:
        await connection.close()
    

async def log_event(msg):
    #print(msg)
    pass


async def is_ignored(msg) -> bool:
    match msg.headers["Event"]:
        case "CardConnect":
            return await is_card_ignored(msg.headers["Id"], msg.headers["Manufacturer"])         
        case "CertFound":
            return await is_cert_ignored(msg.headers["Id"], msg.headers["Issuer"])
        case _:
            return False
