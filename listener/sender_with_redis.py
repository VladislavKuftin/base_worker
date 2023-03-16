import json
import aio_pika
import asyncio
import random
import string
import redis
from tokens_db import save_to_database
from datetime import datetime

from cryptography import x509
from cryptography.hazmat.backends import default_backend

AGENTS_COUNT = 10  # number of agents generating certificates
REJECTED_RATE = 0.5  # share of rejected certificates

STATUS = random.choice(["rejected", "accepted"])

async def publish_message(loop, message, exchange_name, routing_key):
    connection = await aio_pika.connect_robust("amqp://guest:guest@127.0.0.1/", loop=loop)
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=routing_key
        )
        # print(f" [x] Sent {message}")


def load_certificate(cert_file_name='cert.pem'):
    with open(cert_file_name, 'rb') as f:
        cert_data = f.read()
    cert = x509.load_pem_x509_certificate(cert_data, default_backend())
    return cert


async def create_token(loop, rejected):
    token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    cert_load = load_certificate()
    cert_events = {
        "EventType": "CERT_FOUND",
        "Serial": format(cert_load.serial_number, 'x'),
        "Issuer": cert_load.issuer.rfc4514_string(),
        "Timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        "Hostname": f"device",
        "Username": "jdoe",
        "ManufacturerID": token,
        "Device": "Contoso Ltd.",
        "Body": "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",
    }
    card_events = {
        "EventType": "CARD_CONNECTED",
        "Serial": token,  # используем значение переменной token
        "ManufacturerID": "Acme Corp",
        "Timestamp": "2022-12-01 10:30:00",
        "Hostname": "example.com",
        "Username": "john.doe",
        "Label": "Test Card",
        "Model": "Test Model",
        "Flags": "none",
        "MaxPinLen": "4",
        "MinPinLen": "4",
        "TotalPublicMemory": "1024",
        "FreePublicMemory": "512",
        "TotalPrivateMemory": "512",
        "FreePrivateMemory": "256",
        "HardwareVersion": {
            "Major": "1",
            "Minor": "0"
        },
        "FirmwareVersion": {
            "Major": "1",
            "Minor": "0"
        },
        'status': STATUS
    }
    message = {
        "CERT_EVENTS": [cert_events],
        "CARD_EVENTS": [card_events]
    }
    await publish_message(loop, message, "", "agent_event")
    return token


async def add_tokens():
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    # Generate tokens with statuses
    # tokens = []
    # for _ in range(AGENTS_COUNT):
    #     rejected = random.random() < REJECTED_RATE
    #     token = await create_token(asyncio.get_running_loop(), rejected)
    #     tokens.append((token, 'rejected' if rejected else 'accepted'))

    

    # Add tokens to Redis cache and database
    for token, status in create_token():
        if status == 'rejected':
            redis_client.set(token, status)
        elif status == "accepted":
            save_to_database(token, status)


if __name__ == '__main__':
    asyncio.run(add_tokens())
