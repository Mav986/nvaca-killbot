import requests

from esipy import App, EsiClient
from esipy.cache import FileCache

import config

esiapp = App.create(config.ESI_SWAGGER_JSON)

esiclient = EsiClient(
    # cache=RedisCache(Redis(config.REDIS_CACHE_HOST, port=config.REDIS_CACHE_PORT)),
    cache=FileCache('.webcache'),
    headers={'User-Agent': config.ESI_USER_AGENT}
)


def get_system(system_id):
    """
    Get system details for a system id from ESI
    :param system_id: ID for the required system
    :return: Dictionary containing system details
    """
    op = esiapp.op['get_universe_systems_system_id'](system_id=system_id)

    res = esiclient.request(op)

    if res.status == 200:
        return res.data
    else:
        return None


def get_constellation(constellation_id):
    """
    Get constellation details for a constellation id from ESI
    :param constellation_id: ID for the required constellation
    :return: Dictionary containing constellation details
    """
    op = esiapp.op['get_universe_constellations_constellation_id'](constellation_id=constellation_id)

    res = esiclient.request(op)

    if res.status == 200:
        return res.data
    else:
        return None


def get_region(region_id):
    """
    Get region details for a region id from ESI
    :param region_id: ID for the required region
    :return: Dictionary containing region details
    """
    op = esiapp.op['get_universe_regions_region_id'](region_id=region_id)

    res = esiclient.request(op)

    if res.status == 200:
        return res.data
    else:
        return None


def get_character(character_id):
    op = esiapp.op['get_characters_character_id'](character_id=character_id)

    res = esiclient.request(op)

    if res.status == 200:
        return res.data
    else:
        return None


def get_corporation(corporation_id):
    op = esiapp.op['get_corporations_corporation_id'](corporation_id=corporation_id)

    res = esiclient.request(op)

    if res.status == 200:
        return res.data
    else:
        return None


def get_name(id):
    op = esiapp.op['post_universe_names'](ids=[id])

    res = esiclient.request(op)

    if res.status == 200:
        return res.data[0]
    else:
        return None


def get_faction_corp(id):
    op = esiapp.op['get_universe_factions']()

    res = esiclient.request(op)


    if res.status == 200:
        factions = res.data
        corp_id = [f['corporation_id'] for f in factions if f['faction_id'] == id][0]
        corp = get_corporation(corp_id)
        return {'corporation_id':corp_id, **corp}
    else:
        return None


def get_system_region(system_id):
    """
    Get the region for a system id via system -> constellation.
    :param system_id: System ID to be resolved
    :return: Dictionary containing region details.
    """
    system = get_system(system_id)
    constellation = get_constellation(system.get('constellation_id'))
    region = get_region(constellation.get('region_id'))

    return region


def check_jspace(system_id):
    """
    Get the wormhole class for a given system via system -> constellation -> region
    :param system_id: System ID to be checked
    :return: String of the wormhole class or False for K-Space.
    """
    region = get_system_region(system_id)
    code = region.get('name', 'XX')[0:2]

    return config.JSPACE_REGION_MAP.get(code, False)
