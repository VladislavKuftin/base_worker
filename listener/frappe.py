import aiohttp
from . import config
import json

def frappe_server() -> str:
    server = config.FRAPPE_PROTOCOL + "://" + config.FRAPPE_SERVER
    if config.FRAPPE_PORT != None:
        server = server + ":" + str(config.FRAPPE_PORT)
    #print(server)
    return server

async def create_card_request(msg):
    print(config.FRAPPE_SERVER)
    async with aiohttp.ClientSession() as session:
            body = json.loads(msg.body)
            async with session.post(frappe_server()+"/api/resource/Card", json={
                    'serial': msg.headers["Id"],
                    'manufacturer': msg.headers["Manufacturer"],
                    'found': str(msg.timestamp),
                    'hostname': msg.headers["Hostname"],
                    'username': msg.headers["Username"],
                    'label': body['Label'],
                    'model': body['Model'],
                    'card_flags': body['Flags'],
                    'maxpinlen': body['MaxPinLen'],
                    'minpinlen': body['MinPinLen'],
                    'totalpublicmemory': body['TotalPublicMemory'],
                    'freepublicmemory': body['FreePublicMemory'],
                    'totalprivatememory': body['TotalPrivateMemory'],
                    'freeprivatememory': body['FreePrivateMemory'],
                    'hardwareversionmajor': body['HardwareVersion']['Major'],
                    'hardwareversionminor': body['HardwareVersion']['Minor'],
                    'firmwareversionmajor': body['FirmwareVersion']['Major'],
                    'firmwareversionminor': body['FirmwareVersion']['Minor'],                    
                    'status': 'Pending'
                    
                }, headers = {
                    'Authorization': "token "+ config.FRAPPE_API_KEY + ":" + config.FRAPPE_API_SECRET
                }) as resp:
                """if resp.status==200:
                    rv = await IgnoredCard.create(
                        serial=msg.headers["Id"],
                        manufacturer = msg.headers["Manufacturer"],
                        pending = True
                        )
                """
                print(await resp.text())


async def create_cert_request(msg):
    pass