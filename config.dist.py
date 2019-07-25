###################################
# List of Alliance- and Corp IDs
###################################
AFFILIATIONS = [98323701, 99006113, 99009324]

###################################
# ESI Settings
###################################
ESI_DATASOURCE = 'tranquility'
ESI_SWAGGER_JSON = 'https://esi.evetech.net/_latest/swagger.json?datasource={}'.format(ESI_DATASOURCE)
ESI_USER_AGENT = 'USER-AGENT-HERE'

###################################
# Formatting settings
###################################
COLOR_KILL = 3581519
COLOR_LOSS = 13631488

###################################
# Discord settings
###################################
TOKEN = 'DISCORD-TOKEN-HERE'
KILLBOT_CHANNEL_ID = 545986941976576030

###################################
# RedisQ Settings
###################################
REDISQ_TTW = 5 # Time to wait in seconds
REDISQ_QUEUE_ID= 'Killbot' # ID to use for identifying with RedisQ
REDISQ_URL = 'https://redisq.zkillboard.com/listen.php?queueID={queueID}&ttw={ttw}'.format(queueID=REDISQ_QUEUE_ID,
                                                                                           ttw=REDISQ_TTW)

###################################
# Region names defined as JSpace
###################################
JSPACE_REGION_MAP = {
    'A-':'C1',
    'B-':'C2',
    'C-':'C3',
    'D-':'C4',
    'E-':'C5',
    'F-':'C6',
    'G-':'C12',
    'H-':'C13'
}