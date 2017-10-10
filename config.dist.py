###################################
# List of Alliance- and Corp IDs
###################################
AFFILIATIONS = [98323701, 99006113]

###################################
# ESI Settings
###################################
ESI_DATASOURCE = 'tranquility'
ESI_SWAGGER_JSON = 'https://esi.tech.ccp.is/latest/swagger.json?datasource={}'.format(ESI_DATASOURCE)
ESI_USER_AGENT = 'change me'


###################################
# Formatting settings
###################################
COLOR_KILL = '#36a64f'
COLOR_LOSS = '#d00000'

###################################
# Slack settings
###################################
WEBHOOK_URL = 'https://hooks.slack.com/services/team/app/key'

###################################
# RedisQ Settings
###################################
REDISQ_URL = 'https://redisq.zkillboard.com/listen.php?queueID={queueID}&ttw={ttw}'
REDISQ_TTW = 5 # Time to wait in seconds
REDISQ_QUEUE_ID= 'Killbot' # ID to use for identifying with RedisQ



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