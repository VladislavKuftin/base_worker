import asyncpg


conn = None

async def get_connect():
    global conn
    if conn == None:
        conn = await asyncpg.connect("postgresql://postgres:postgres@localhost/_5d59773de681e07f")
    return conn

async def is_card_ignored(serial: str, manufacturer: str) -> bool:
    conn = await get_connect()
    row = await conn.fetchrow(
        'SELECT * FROM "tabCard" WHERE serial = $1 and manufacturer = $2', serial, manufacturer)
    return (not (row == None))

async def is_cert_ignored(serial: str, issuer: str) -> bool:
    conn = await get_connect()
    row = await conn.fetchrow(
        'SELECT * FROM "tabCertificate" WHERE serial = $1 and issuer = $2', serial, issuer)
    return (not (row == None))
