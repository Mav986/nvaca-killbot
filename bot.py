import logging
import sys
import requests

import config
import redisq

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create a file handler
# handler = logging.FileHandler('debug.log')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

def run():
    running = True
    logger.info('Bot is listening on RedisQ')
    while running:
        try:
            kill = redisq.fetch_kill(config.REDISQ_QUEUE_ID, config.REDISQ_TTW)

            if not kill:
                continue

            if redisq.filter_affiliation(kill):
                json=redisq.format_kill(kill)
                r = requests.post(config.WEBHOOK_URL, json=json)
                logger.debug(r, json)

        except KeyboardInterrupt:
            logger.info('Received Keyboard interrupt.')
            running = False
        except Exception as e:
            logger.exception(e)


if __name__ == '__main__':
    run()