import asyncpg
from . import config

conn = None

async def get_connect():
    global conn
    if conn == None:
        conn = await asyncpg.connect(str(config.DB_DSN))
    return conn

async def is_card_ignored(serial: str, manufacturer: str) -> bool:
    conn = await get_connect()
    row = await conn.fetchrow(
        'SELECT * FROM "tabCard" WHERE serial = $1 and manufacturer = $2', serial, manufacturer)
    return (not (row == None))

async def is_cert_ignored(serial: str, manufacturer: str) -> bool:
    conn = await get_connect()
    return False
