import requests

import config


def get_system(system_id):
    """
    Get system details for a system id from ESI
    :param system_id: ID for the required system
    :return: Dictionary containing system details
    """
    uri = '{base_url}/v3/universe/systems/{system_id}/?datasource={datasource}&language=en-us'.format(
        base_url=config.ESI_URL, system_id=system_id, datasource=config.ESI_DATASOURCE
    )

    res = requests.get(uri)

    if res.status_code == 200:
        return res.json()
    else:
        return None


def get_constellation(constellation_id):
    """
    Get constellation details for a constellation id from ESI
    :param constellation_id: ID for the required constellation
    :return: Dictionary containing constellation details
    """
    uri = '{base_url}/v1/universe/constellations/{constellation_id}/?datasource={datasource}&language=en-us'.format(
        base_url=config.ESI_URL, constellation_id=constellation_id, datasource=config.ESI_DATASOURCE
    )

    res = requests.get(uri)

    if res.status_code == 200:
        return res.json()
    else:
        return None


def get_region(region_id):
    """
    Get region details for a region id from ESI
    :param region_id: ID for the required region
    :return: Dictionary containing region details
    """
    uri = '{base_url}/v1/universe/regions/{region_id}/?datasource={datasource}&language=en-us'.format(
        base_url=config.ESI_URL, region_id=region_id, datasource=config.ESI_DATASOURCE
    )

    res = requests.get(uri)

    if res.status_code == 200:
        return res.json()
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
