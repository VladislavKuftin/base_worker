import asyncio
from listener.rabbitmq import setup_rabbitmq


if __name__ == "__main__":
    loop = asyncio.new_event_loop()   
    loop.run_until_complete(setup_rabbitmq(loop))
