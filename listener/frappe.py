import aiohttp
from . import config
import json
from cryptography.x509 import load_pem_x509_certificate


def frappe_server() -> str:
    server = config.FRAPPE_PROTOCOL + "://" + config.FRAPPE_SERVER
    if config.FRAPPE_PORT != None:
        server = server + ":" + str(config.FRAPPE_PORT)
    print(server)
    return server


frappe_server()


async def create_card_request(msg):
    async with aiohttp.ClientSession() as session:
        info = json.dumps(msg)
        body = json.loads(info)
        if msg["status"] == "accepted":
            async with session.post(frappe_server() + "/api/resource/Card", json={
                'serial': msg["Serial"],
                'manufacturer': msg["ManufacturerID"],
                'found': msg["Timestamp"],
                'hostname': msg["Hostname"],
                'username': msg["Username"],
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

            }, headers={
                'Authorization': "token " + config.FRAPPE_API_KEY + ":" + config.FRAPPE_API_SECRET
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
    async with aiohttp.ClientSession() as session:
        body = "-----BEGIN CERTIFICATE-----\n" + msg["Body"] + "\n-----END CERTIFICATE-----"
        cert = load_pem_x509_certificate(body.encode(encoding='UTF-8'))
        # print(cert.subject.rfc4514_string())
        async with session.post(frappe_server() + "/api/resource/Certificate", json={
            'serial': msg["Serial"],
            'issuer': msg["Issuer"],
            'found': msg["Timestamp"],
            'hostname': msg["Hostname"],
            'username': msg["Username"],
            'card_serial': msg["ManufacturerID"],
            'card_manufacturer': msg["Device"],
            'body': msg["Body"],
            'not_valid_before': str(cert.not_valid_before),
            'not_valid_after': str(cert.not_valid_after),
            'subject': cert.subject.rfc4514_string(),
            'status': 'Pending'

        }, headers={
            'Authorization': "token " + config.FRAPPE_API_KEY + ":" + config.FRAPPE_API_SECRET
        }) as resp:
            print(await resp.text())

