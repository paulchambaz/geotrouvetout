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

def get_position_data(lat, lon, radius, max_age, use_cache):
    """
    Get open street map data from latitude and longitude.

    @param lat The latitude to look around.
    @param lon The longitude to look around.
    @param radius The size of the area to look around.
    @param max_age Maximum age for a request to be valid in the cache, -1 to
    ignore.
    @param use_cache Wether or not to use the cache for this request.
    """
    logging.info("get_position_data")

    # format proper query
    query = f"""
    [out:json];
    node({lat - radius / 2},{lon - radius / 2},{lat + radius / 2},{lon + radius
/ 2});
    out center;
    """
      # node(around:5000,{lat},{lon})["name"]["addr:street"]["highway"];
      # way(around:5000,{lat},{lon})["name"]["addr:street"]["highway"];

    # load cache
    cache = load_cache("cache.json")

    if is_in_cache(query, cache):
        # get result from cache
        result = cache_query(query, cache)
    else:
        # get result from overpass api
        api = overpy.Overpass()
        result = api.query(query)

    # save result to cache
    save_query(query, result, cache)
    save_cache(cache, "cache.json")

    # format result to proper dict

    # return resulting dict


def get_town_data(town, max_age, use_cache):
    """
    Get open street map data from a town name.

    @param town The town to look around.
    @param max_age Maximum age for a request to be valid in the cache, -1 to
    ignore.
    @param use_cache Wether or not to use the cache for this request.
    """
    print("get_town_data")

    # format proper query
    query = f"""
    [out:json];
    """

    # load cache
    cache = load_cache("cache.json")

    if is_in_cache(query, cache):
        # get result from cache
        result = cache_query(query, cache)
    else:
        # get result from overpass api
        api = overpy.Overpass()
        result = api.query(query)

    # save result to cache
    save_query(query, result, cache)
    save_cache(cache, "cache.json")

    # format result to proper dict

    # return resulting dict


def get_road_data(road, max_age, use_cache):
    """
    Get open street map data from a street name.

    @param street The street to look around.
    @param max_age Maximum age for a request to be valid in the cache, -1 to
    ignore.
    @param use_cache Wether or not to use the cache for this request.
    """
    print("get_road_data")

    # format proper query
    query = f"""
    [out:json];
    """

    # load cache
    cache = load_cache("cache.json")

    if is_in_cache(query, cache):
        # get result from cache
        result = cache_query(query, cache)
    else:
        # get result from overpass api
        api = overpy.Overpass()
        result = api.query(query)

    # save result to cache
    save_query(query, result, cache)
    save_cache(cache, "cache.json")

    # format result to proper dict

    # return resulting dict


def is_in_cache(query: str, cache: dict[str, any]) -> bool:
    """
    Returns if a query is in the cache.

    @param query The query to check for.
    @param cache The cache.
    @retrun Wether or not the query is in the cache.
    """
    print("is_in_cache")
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
    print("cache_query")
    query_hash = hashlib.md5(query.encode()).hexdigest()

    return cache[query_hash]


def save_query(query, str, result: any, cache: dict[str, any]):
    """
    Saves the result of a query in the cache.

    @param query The query.
    @param result The result of the query.
    @param cache The cache.
    """
    print("save_query")
    query_hash = hashlib.md5(query.encode()).hexdigest()

    cache[query_hash] = result


def load_cache(cache_file: str) -> dict[str, any]:
    """
    Loads the cache file.

    @param cache_file Path to the cache file.
    @return The dict of the cache.
    """
    print("load_cache")
    with open(cache_file, "r", encoding="utf-8") as file:
        return json.load(file)


def save_cache(cache: dict[str, any], cache_file: str):
    """
    Saves the cache to the cache file.

    @param cache The cache.
    @param cache_file The path to the cache file.
    """
    print("save_cache")
    with open(cache_file, "w", encoding="utf-8") as file:
       json.dump(cache, file) 
