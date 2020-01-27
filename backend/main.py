import asyncio
import aiohttp
from aiohttp import web
import ssl
import os
import sys

from bot import GetUpdate

if 'TOKEN' not in os.environ or 'EXTERNAL_ADDRESS' not in os.environ or 'EXTERNAL_PORT' not in os.environ:
    print('REQUIRED VARIABLES NOT SET (TOKEN or EXTERNAL_ADDRESS or EXTERNAL_PORT)')
    sys.exit()

async def set_webhook(token, external_address, external_port):
    # set webhook (url with sert for receive updates from telegram)
    headers = {'content-type': 'multipart/form-data'}
    session = aiohttp.ClientSession(connector = aiohttp.TCPConnector(ssl = False));
    api_url = 'https://api.telegram.org/bot{}/'.format(token)
    webhook_url = 'https://{}:{}/bot/{}'.format(external_address, external_port, token)
    print(webhook_url)
    await session.post(api_url + 'setWebhook?url='+webhook_url, data={'certificate':open('ssl/iontzev-bot-public.pem', 'rb')})
    await session.close()

if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    app = web.Application()

    app.token = os.environ.get('TOKEN')
    external_address = os.environ.get('EXTERNAL_ADDRESS')
    external_port = os.environ.get('EXTERNAL_PORT')
        
    # set webhook - need once
    loop.run_until_complete(set_webhook(app.token, external_address, external_port))

    app.chats = {}

    # make routes
    app.router.add_route('POST', '/bot/{}'.format(app.token), GetUpdate)

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain('ssl/iontzev-bot-public.pem', 'ssl/iontzev-private.key')

    web.run_app(app, port=8443, ssl_context=ssl_context)


