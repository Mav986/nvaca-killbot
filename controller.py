import requests
import esi

from datetime import datetime
import logging
from discord import Embed
from config import REDISQ_URL, AFFILIATIONS, COLOR_KILL, COLOR_LOSS



async def fetch_kill():
    """
    Fetch a single kill from RedisQ.
    :return: Kill object
    """
    r = requests.get(REDISQ_URL)

    if r.status_code == 200:
        return r.json().get('package', None)
    else:
        r.raise_for_status()


async def filter_affiliation(kill):
    """
    Filter method to check whether any characters associated with the kill are in the affiliations list.
    Intended to be used with `filter()`
    :param kill: Kill object from RedisQ
    :return: True if the victim or any attacker are in any of the alliances or corps passed, False otherwise
    """
    affiliations = AFFILIATIONS
    result = False

    killmail = kill.get('killmail', {})

    result |= await _is_friendly(killmail.get('victim', {}), affiliations)

    for attacker in killmail.get('attackers', []):
        result |= await _is_friendly(attacker, affiliations)

    return result


async def post_kill(channel, kill):
    """
    Post a kill to a discord channel
    :param channel: Channel object from Discord.py
    :param kill: Kill object from RedisQ
    """
    embed = await format_kill(kill)
    await channel.send(embed=embed)
    logging.getLogger('__main__').info(kill)


async def _is_friendly(character, affiliations):
    """
    Check if character is a member of a list of corps and / or alliances
    :param character: Character object from RedisQ
    :param affiliations: List of Corp or Alliance IDs
    :return: True if character is affiliated with any of the IDs, False otherwise
    """
    result = False

    result |= character.get('alliance_id', False) in affiliations
    result |= character.get('corporation_id', False) in affiliations

    return result

async def format_kill(kill):
    """
    Format the kill for display on discord
    :param kill: Kill object from RedisQ
    :return: Dictionary that can be converted to an Embed object for discord
    """

    # Collect killmail data
    kill_id = kill.get('killID', {})
    killmail = kill.get('killmail', {})
    zkb = kill.get('zkb', {})

    # Format kill data
    victim, ship_raw, damage_taken = await get_victim_data(killmail)
    killer, num_attackers = await get_attacker_data(killmail)
    top_attacker = await get_top_attacker(killmail)
    location = await get_location_data(killmail)
    value = "{:,.0f}".format(zkb.get('totalValue', 0))
    is_loss = await _is_friendly(victim, AFFILIATIONS)

    if is_loss:
        description = await create_description(victim, killer, ' was killed by ')
        color = COLOR_LOSS
    else:
        description = await create_description(killer, victim, ' killed ')
        color = COLOR_KILL

    # Create required markdown hyperlinks
    ship = await _build_markdown_hyperlink(ship_raw['name'], 'https://zkillboard.com/ship/' + str(ship_raw['type_id']))

    # Set up embed fields
    fields = [
        await format_field("Damage taken", damage_taken),
        await format_field("Pilots involved", num_attackers),
        await format_field("Value", value),
        await format_field("Ship", ship),
        await format_field("Most damage", top_attacker, inline=False),
        await format_field("System", location, inline=False)
    ]

    # Collect data into a dict to be converted to an embed object
    kill_dict = {
        "description": description,
        "color": color,
        "fields": fields,
        "thumbnail": {
            "url": "https://imageserver.eveonline.com/Render/{}_64.png".format(
            victim.get('ship_type_id', {}))
        },
        "killmail": {
            "text": "**Kill: " + ship_raw['name'] + "**",
            "url": "https://zkillboard.com/kill/{}".format(kill_id)
        },
        "timestamp": datetime.strptime(killmail.get('killmail_time'), '%Y-%m-%dT%H:%M:%SZ')
    }

    return await _build_embed(kill_dict)


async def get_victim_data(killmail):
    """
    Collect victim data from a killmail
    :param killmail: killmail object from RedisQ
    :return: the victim, the ship they were flying, and the damage they took
    """
    victim_raw = killmail.get('victim', {})
    victim = await get_party_details(victim_raw)

    ship_raw = esi.get_type(victim.get('ship_type_id'))

    damage_taken = victim.get("damage_taken", 0)

    return victim, ship_raw, "{:,.0f}".format(damage_taken)


async def get_ship_name(victim_ship):
    """
    Get the name of the victim's ship
    :param victim_ship: JSON containing data for the victim's ship
    :return: A markdown hyperlink linking the ship name to its zkill URL
    """
    if victim_ship:
        return await _build_markdown_hyperlink(victim_ship['name'], 'https://zkillboard.com/ship/' + str(victim_ship['type_id']))
    else:
        return 'Unknown'


async def get_party_details(party):
    """
    Get character info, substitute char name with ship type for nameless NPCs
    Corp name substituted with faction default corp if corp missing and faction available.
    both set to Unknown if neither of the above apply.
    :param party:
    :return:
    """
    if 'character_id' in party:
        party['details'] = esi.get_character(party.get('character_id'))
        party['zkb_link'] = 'https://zkillboard.com/character/{}'.format(party.get('character_id'))
    elif 'ship_type_id' in party:
        party['details'] = esi.get_type(party.get('ship_type_id'))
        party['zkb_link'] = 'https://zkillboard.com/ship/{}'.format(party.get('ship_type_id'))
    else:
        party['details'] = {'name': 'Unknown'}
        party['zkb_link'] = '#'

    if 'corporation_id' in party:
        party['corporation'] = esi.get_corporation(party.get('corporation_id'))
        party['corp_zkb_link'] = 'https://zkillboard.com/corporation/{}'.format(party.get('corporation_id'))
    elif 'faction_id' in party:
        try:
            party['corporation'] = esi.get_faction_corp(party.get('faction_id'))
            party['corp_zkb_link'] = 'https://zkillboard.com/corporation/{}'.format(
                party['corporation'].get('corporation_id'))
        except ValueError:
            party['corporation'] = {'name': 'Unknown'}
            party['corp_zkb_link'] = '#'
    else:
        party['corporation'] = {'name': 'Unknown'}
        party['corp_zkb_link'] = 'https://zkillboard.com/faction/{}/'.format(party.get('faction_id'))

    return party


async def get_attacker_data(killmail):
    """
    Collect attacker data from a killmail
    :param killmail: killmail object from RedisQ
    :return: The attacker who dealt the final blow, and the total number of attackers
    """
    attackers = killmail.get('attackers', [])

    killer_raw = await get_killer(attackers)
    killer = await get_party_details(killer_raw)

    return killer, "{:,.0f}".format(len(attackers))


async def get_killer(attackers):
    """
    Get the attacker who dealt the final blow
    :param attackers: a collection of attackers
    :return: The killer's data in JSON form
    """
    return [a for a in attackers if a['final_blow']][0]


async def get_top_attacker(killmail):
    """
    Collect top contributor data from a killmail
    :param killmail: killmail object from RedisQ
    :return: a string with the top attacker's name and the damage they dealt
    """
    attackers = killmail.get('attackers', [])

    top_contribution_raw = await get_max_dmg(attackers)
    top_contribution = await get_party_details(top_contribution_raw)

    top_attacker = await _build_markdown_hyperlink(top_contribution['details']['name'], top_contribution['zkb_link'])
    dmg_done = top_contribution['damage_done']

    return top_attacker + ' ({:,.0f})'.format(dmg_done)


async def get_max_dmg(attackers):
    """
    Get the attacker who dealt the most damage
    :param attackers: a collection of attackers
    :return: The top damage attacker's data in JSON form
    """
    return [a for a in attackers if a.get('damage_done', 0) == max([atk.get('damage_done', 0) for atk in attackers])][0]


async def _build_markdown_hyperlink(text, url):
    """
    Convert text and url into a markdown hyperlink
    :param text: the text to display
    :param url: the website the text links to
    :return: a markdown hyperlink string
    """
    return '[' + text + '](' + url + ')'


async def get_location_data(killmail):
    """
    Determines whether a System is in Wormhole space or Known space and produces a formatted location field accordingly
    :param killmail: killmail with location data from
    :return: Text content for the System field in the killmail response
    """
    system_id = killmail.get('solar_system_id')
    region = esi.get_system_region(system_id)
    wspace = esi.check_jspace(system_id)
    solar_system_details = esi.get_system(system_id)
    security = round(solar_system_details['security_status'], 1)

    system = await _build_markdown_hyperlink(solar_system_details['name'], 'https://zkillboard.com/system/' + str(solar_system_details['system_id']))
    region = await _build_markdown_hyperlink(region['name'], 'https://zkillboard.com/region/' + str(region['region_id']))

    if wspace:
        system += '(' + wspace + ')'

    result = system + ' (' + str(security) + ') / ' + region

    return result


async def create_description(victim, killer, action):
    """
    Create a discord embed description from the victim's and killer's data
    :param victim: the victim's data in JSON form
    :param killer: the killer's data in JSON form
    :param action: the action which took place, either 'killed' or 'was killed by' depending on affiliation
    :return:
    """
    victim_name = await _build_markdown_hyperlink(victim['details']['name'], victim['zkb_link'])
    killer_name = await _build_markdown_hyperlink(killer['details']['name'], killer['zkb_link'])
    killer_corp = await _build_markdown_hyperlink(killer['corporation']['name'], killer['corp_zkb_link'])

    return victim_name + action + killer_name + ' (' + killer_corp + ')'


async def format_field(name, value, inline=True):
    """
    Format an attachment field for Discord messages
    :param name: Field title
    :param value: Field text
    :param inline: Whether the field should be rendered in two column style
    :return: Dictionary ready to be converted to JSON for display in Discord.
    """
    return {
        "name": name,
        "value": value,
        "inline": inline
    }


async def _build_embed(json):
    """
    Build a Discord embed object from json
    :param json: json to be converted
    :return: a Discord embed object
    """
    embed =  Embed(
        description=json['description'],
        color=json['color'],
        timestamp=json['timestamp'],
        title=json['killmail']['text'],
        url=json['killmail']['url']
    ).set_thumbnail(
        url=json['thumbnail']['url']
    )
    # .set_author(
    #     name=json['author']['name'],
    #     url=json['author']['url'],
    #     icon_url=json['author']['icon_url']
    # )

    for field in json['fields']:
        embed.add_field(
            name=field['name'],
            value=field['value'],
            inline=field['inline']
        )

    return embed