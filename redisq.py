import requests

import config
import esi


def check_affiliation(character, affiliations):
    """
    Check if character is a member of a list of corps and / or alliances
    :param character: Character object from RedisQ
    :param affiliations: List of Corp- or Alliance IDs
    :return: True if character is affiliated with any of the IDs, False otherwise
    """
    result = False

    if 'alliance' in character:
        result |= character['alliance']['id'] in affiliations
    if 'corporation' in character:
        result |= character['corporation']['id'] in affiliations

    return result


def fetch_new_kills(queueID, ttw):
    """
    Refresh kills from RedisQ. Loops request until a null package is received.
    :param queueID: ID used to identify client on RedisQ
    :param ttw: Time in seconds to wait before receiving a Null package
    :return: List of kill objects
    """
    url = config.REDISQ_URL.format(queueID=queueID, ttw=ttw)

    kills = []

    while True:
        r = requests.get(url).json()
        if r['package'] == None:
            break

        kills.append(r['package'])

    return kills


def filter_association(kill):
    """
    Filter method to check whether any characters associated with the kill are in the affiliations list.
    Intended to be used with `filter()`
    :param kill: Kill object from RedisQ
    :return: True if the victim or any attacker are in any of the alliances or corps passed, False otherwise
    """
    affiliations = config.AFFILIATIONS
    result = False

    killmail = kill.get('killmail')

    result |= check_affiliation(killmail.get('victim', {}), affiliations)

    for attacker in killmail.get('attackers', []):
        result |= check_affiliation(attacker, affiliations)

    return result


def format_kill(kill):
    """
    Format the kill for display on slack
    :param kill: Kill object from RedisQ
    :return: Dictionary that can be dumped into json format codes for slack message
    """
    killID = kill['killID']
    killmail = kill.get('killmail')
    victim = killmail.get('victim')
    loss = check_affiliation(victim, config.AFFILIATIONS)
    attackers = killmail.get('attackers', {})
    killer = [a for a in attackers if a['finalBlow']][0]
    maxDmg = [a for a in attackers if a.get('damageDone', 0) == max([atk.get('damageDone', 0) for atk in attackers])][0]
    solarSystem = killmail.get('solarSystem')
    region = esi.get_system_region(solarSystem.get('id', 0))
    zkb = kill.get('zkb')

    wspace = esi.check_jspace(solarSystem.get('id', 0))

    if not wspace:
        systemDetails = esi.get_system(solarSystem.get('id', 0))
        system = "<https://zkillboard.com/system/{solarSystem[id]}|{solarSystem[name]}> " \
                 "({systemDetails[security_status]:.2f})/ " \
                 "<https://zkillboard.com/region/{region[region_id]}|{region[name]}>".format(solarSystem=solarSystem,
                                                                                             region=region,
                                                                                             systemDetails=systemDetails)
    else:
        system = "<https://zkillboard.com/system/{solarSystem[id]}|{solarSystem[name]}> ({wspace})/ " \
                 "<https://zkillboard.com/region/{region[region_id]}|{region[name]}>".format(solarSystem=solarSystem,
                                                                                             region=region,
                                                                                             wspace=wspace)

    if loss:
        title = "{victim[character][name]} was killed by {killer[character][name]} ({killer[corporation][name]})"
    else:
        title = "{killer[character][name]} killed {victim[character][name]} ({victim[corporation][name]})"

    json = {
        "attachments": [
            {
                "fallback": "https://zkillboard.com/kill/{}/".format(killID),
                "color": config.COLOR_LOSS if loss else config.COLOR_KILL,
                "title": title.format(killer=killer, victim=victim),
                "title_link": "https://zkillboard.com/kill/{}".format(killID),
                "fields": [
                    {
                        "title": "Damage taken",
                        "value": victim.get('damageTaken_str', '0'),
                        "short": True
                    },
                    {
                        "title": "Pilots involved",
                        "value": killmail.get('attackerCount_str', '0'),
                        "short": True
                    },
                    {
                        "title": "Value",
                        "value": '{:,.2f}'.format(zkb.get('totalValue')),
                        "short": True
                    },
                    {
                        "title": "Ship",
                        "value": victim.get('shipType', {}).get('name'),
                        "short": True
                    },
                    {
                        "title": "Most damage",
                        "value": "<https://zkillboard.com/character/{mostDmg[character][id]}|{mostDmg[character][name]}>"
                                 "({mostDmg[damageDone]})".format(mostDmg=maxDmg),
                        "short": False
                    },
                    {
                        "title": "System",
                        "value": system,
                        "short": False
                    }
                ],
                "thumb_url": "https://imageserver.eveonline.com/Render/{shipType[id]}_64.png".format(
                    shipType=victim.get('shipType', {})),
            }
        ]
    }

    return json
