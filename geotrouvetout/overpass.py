import os
import json
import logging
import hashlib
import overpy

# TODO: cache system works but would benefit for a little added complexity
# first it would be good to rewrite the get functions so that you can omit
# cache use
# second the cache structure should be changed so that each hash can have an
# age we can then pass a max age to the cache
# -1 dont use that information -> always return the cache
# >= 0 -> only return the cache if the current age is is younger than the cache
# age + max age

def get_position_data(latitude, longitude, max_age=365, use_cache=True):
    """
    Get open street map data from latitude and longitude.

    @param latitude The latitude to look around.
    @param longitude The longitude to look around.
    @param max_age Maximum age for a request to be valid in the cache, -1 to
    ignore.
    @param use_cache Wether or not to use the cache for this request.
    """
    logging.info("get_position_data")

    # format proper query
    query = f"""[out:json];
// input coordinates
is_in({latitude},{longitude})->.searchArea;
area.searchArea[name][admin_level=2]->.country;
area.searchArea[name][admin_level=8]->.town;

// find streets and buildings in the town
way(area.town)[highway][name]->.streets;
way(area.town)[building][name]->.buildings;

// find natural features in the town
way(area.town)[natural]->.naturalFeatures;

// find land use information in the town
way(area.town)[landuse]->.landuse;

// returning result
.country out body;
.town out body;
.streets out body;
.buildings out body;
.naturalFeatures out body;
.landuse out body;"""

    # load cache
    cache = load_cache("cache.json")

    if is_in_cache(query, cache) and use_cache:
        logging.info("query is in the cache")
        # get result from cache
        result = cache_query(query, cache)
    else:
        logging.info("making query to open street map")
        # get result from overpass api
        api = overpy.Overpass()
        data = api.query(query)

        # format result to proper dict
        result = process_result(data)

    # save result to cache
    save_query(query, result, cache)
    save_cache(cache, "cache.json")

    # return resulting dict
    return result

def get_town_data(town, max_age=365, use_cache=True):
    """
    Get open street map data from a town name.

    @param town The town to look around.
    @param max_age Maximum age for a request to be valid in the cache, -1 to
    ignore.
    @param use_cache Wether or not to use the cache for this request.
    """
    logging.info("get_town_data")

    # format proper query
    query = f"""[out:json];

// input town name
area[name="{town}"][admin_level=8]->.town;
area.town[name][admin_level=2]->.country;

// find streets and buildings in the town
way(area.town)[highway][name]->.streets;
way(area.town)[building][name]->.buildings;

// find natural features in the town
way(area.town)[natural]->.naturalFeatures;

// find land use information in the town
way(area.town)[landuse]->.landuse;

// returning result
.country out body;
.town out body;
.streets out body;
.buildings out body;
.naturalFeatures out body;
.landuse out body;"""

    # load cache
    cache = load_cache("cache.json")

    if is_in_cache(query, cache) and use_cache:
        logging.info("query is in the cache")
        # get result from cache
        result = cache_query(query, cache)
    else:
        logging.info("making query to open street map")
        # get result from overpass api
        api = overpy.Overpass()
        data = api.query(query)

        # format result to proper dict
        result = process_result(data)

    # save result to cache
    save_query(query, result, cache)
    save_cache(cache, "cache.json")

    # return resulting dict
    return result

def process_result(result):
    data = {
        "country": None,
        "town": None,
        "streets": [],
        "buildings": [],
        "naturalFeatures": [],
        "landuse": []
    }

    # Process country and town
    for area in result.areas:
        if area.tags.get("admin_level") == "2":
            data["country"] = area.tags.get("name")
        elif area.tags.get("admin_level") == "8":
            data["town"] = area.tags.get("name")

    # Process streets
    for way in result.ways:
        if "highway" in way.tags and "name" in way.tags:
            data["streets"].append(way.tags["name"])

    # Process buildings
    for way in result.ways:
        if "building" in way.tags and "name" in way.tags:
            data["buildings"].append(way.tags["name"])

    # Process natural features
    for way in result.ways:
        if "natural" in way.tags:
            data["naturalFeatures"].append(way.tags["natural"])

    for rel in result.relations:
        if "natural" in rel.tags:
            data["naturalFeatures"].append(rel.tags["natural"])

    # Process landuse
    for way in result.ways:
        if "landuse" in way.tags:
            data["landuse"].append(way.tags["landuse"])

    for rel in result.relations:
        if "landuse" in rel.tags:
            data["landuse"].append(rel.tags["landuse"])

    # Deduplicate lists
    for key in ["streets", "buildings", "naturalFeatures", "landuse"]:
        data[key] = list(set(data[key]))

    return data


def is_in_cache(query: str, cache: dict[str, any]) -> bool:
    """
    Returns if a query is in the cache.

    @param query The query to check for.
    @param cache The cache.
    @retrun Wether or not the query is in the cache.
    """
    logging.info("is_in_cache")
    query_hash = hashlib.md5(query.encode()).hexdigest()

    if query_hash in cache:
        return True
    else:
        return False


def cache_query(query: str, cache: dict[str, any]) -> any:
    """
    Returns the result of a query from cache.

    @param query The query for return for.
    @param cache The cache.
    @return The result of the request from the cache.
    """
    logging.info("cache_query")
    query_hash = hashlib.md5(query.encode()).hexdigest()

    return cache[query_hash]


def save_query(query: str, result: any, cache: dict[str, any]):
    """
    Saves the result of a query in the cache.

    @param query The query.
    @param result The result of the query.
    @param cache The cache.
    """
    logging.info("save_query")
    query_hash = hashlib.md5(query.encode()).hexdigest()

    cache[query_hash] = result


def load_cache(cache_file: str) -> dict[str, any]:
    """
    Loads the cache file.

    @param cache_file Path to the cache file.
    @return The dict of the cache.
    """
    logging.info("load_cache")
    directory = '/tmp/geotrouvetout'
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, cache_file)

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        return {}


def save_cache(cache: dict[str, any], cache_file: str):
    """
    Saves the cache to the cache file.

    @param cache The cache.
    @param cache_file The path to the cache file.
    """
    logging.info("save_cache")
    directory = '/tmp/geotrouvetout'
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, cache_file)

    with open(filepath, "w", encoding="utf-8") as file:
       json.dump(cache, file) 
