import requests

import config

"""
Killbot message format
{
    "attachments": [
        {
            "fallback": "https://zkillboard.com/kill/{killID}/",
			"color": "#36a64f",
			"title": "{killer.character.name} killed {victim.character.name} (victim.corporation.name)",
			"title_link": "https://zkillboard.com/kill/{killID}",
            "fields": [
				{
					"title": "Damage taken",
					"value": "{victim.damageTaken}",
					"short": true
				},
				{
					"title": "Pilots involved",
					"value": "{attackerCount}",
					"short": true
				},
				{
					"title": "Value",
					"value": "{zkb.totalValue}",
					"short": true
				},
				{
					"title": "Ship",
					"value": "{victim.shipType.name}",
					"short": true
				},
				{
					"title": "Most damage",
					"value": "<https://zkillboard.com/character/{mostDamage.character.id}|{mostDamage.character.name}> ({mostDamage.damageDone})",
					"short": false
				},
				{
					"title": "System",
					"value": "<https://zkillboard.com/system/{solarSystem.id}|{solarSystem.name}> / <https://zkillboard.com/region/{region.id}|{region.name}> / {constellation.name}",
					"short": false
				}
			],
			"image_url": "{victim.shipType.icon.href}"
        }
    ]
}
"""

def check_association(character, associations):
    result = False

    if 'alliance' in character:
        result |= character['alliance']['id'] in associations
    if 'corporation' in character:
        result |= character['corporation']['id'] in associations

    return result


def fetch_new_kills(queueID, ttw):
    url = config.REDISQ_URL.format(queueID = queueID, ttw=ttw)

    kills = []

    while True:
        r = requests.get(url).json()
        if r['package'] == None:
            break

        kills.append(r['package'])

    return kills