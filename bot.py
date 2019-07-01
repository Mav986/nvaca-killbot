import logging
import sys

import discord
client = discord.Client()

from config import KILLBOT_CHANNEL_ID, TOKEN
from controller import fetch_kill, post_kill, filter_affiliation

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

async def listen_for_kills():
    await client.wait_until_ready()
    channel = client.get_channel(KILLBOT_CHANNEL_ID)
    logger.info('Bot is logged in and listening for new kills!')
    while True:
        if not client.is_closed():
            try:
                kill = await fetch_kill()
                if kill and await filter_affiliation(kill):
                    await post_kill(channel, kill)

            except KeyboardInterrupt:
                logger.info('Received Keyboard interrupt.')
            except Exception as e:
                logger.exception(e)
        else:
            client.connect(reconnect=True)


if __name__ == '__main__':
    client.loop.create_task(listen_for_kills())
    client.run(TOKEN)