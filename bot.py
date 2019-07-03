import logging
import sys

import discord
from discord.ext.tasks import loop
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

@loop(seconds=1)
async def listen_for_kills():
    await client.wait_until_ready()
    logger.info('Bot is logged in and listening for new kills!')
    channel = client.get_channel(KILLBOT_CHANNEL_ID)
    while True:
        try:
            if not client.is_closed():
                kill = await fetch_kill()
                if kill and await filter_affiliation(kill):
                    await post_kill(channel, kill)
            else:
                client.connect(reconnect=True)
        except KeyboardInterrupt:
            logger.info('Received Keyboard interrupt.')
        except Exception as e:
            logger.exception(e)


if __name__ == '__main__':
    listen_for_kills.start()
    client.run(TOKEN)