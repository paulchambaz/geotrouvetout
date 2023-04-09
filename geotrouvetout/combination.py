import geotrouvetout
import logging
import pycountry
import json
from collections import defaultdict

# TODO we are using a poor combination method, implement a better one such as
# Bayesian updating approach to combine different sources of information and
# obtain a final confidence level that the image was taken in a specific place
# Use the area probability as a prior probability and then update it using the
# confidence levels derived from the color and language analysis which act as
# likelyhoods


def get_country(image) -> dict[str, float]:
    logging.info("get_country")

    area_weight = 0.1
    color_weight = 0.5
    language_weight = 0.4

    country_codes = [c.alpha_3 for c in pycountry.countries]

    areas = geotrouvetout.get_country_areas()
    if areas:
        area_dict = get_countries_dict(areas, country_codes)
        area_dict = normalize_dict(area_dict)
    else:
        area_dict = empty_dict(country_codes)

    color_analysis = geotrouvetout.get_color_analysis(image)
    if color_analysis:
        color_analysis = amplify_probs(color_analysis, 4)
        color_dict = get_countries_dict(color_analysis, country_codes)
        # color_dict = normalize_dict(color_dict)
    else:
        color_dict = empty_dict(country_codes)

    languages = geotrouvetout.get_languages(image)
    if languages:
        languages = amplify_probs(languages, 4)
        language_dict = get_countries_dict(
            get_country_languages(languages, "stats/country_metadata.json"),
            country_codes,
        )
    else:
        language_dict = empty_dict(country_codes)

    combined_dict = {
        key: (area_dict[key] * color_dict[key] * language_dict[key])
        for key in country_codes
    }

    # return normalize_dict(combined_dict)
    return combined_dict


def get_country_languages(languages, country_metadata_file):
    with open(country_metadata_file, "r") as file:
        country_metadata = json.load(file)
    country_prob = defaultdict(float)
    for lang, prob in languages.items():
        lang_countries = [
            k
            for key, value in country_metadata.items()
            if lang in v["languages"]
        ]
        for country in lang_countries:
            country_prob[country] += prob

    num_langs = len(languages)
    avg_country_prob = {
        key: value / num_langs for k, v in country_prob.items()
    }
    return avg_country_prob


def get_countries_dict(input_dict, country_codes):
    min_value = min(value for value in input_dict.values() if value > 0)
    default_dict = {
        country_code: min_value / 2 for country_code in country_codes
    }
    default_dict.update(input_dict)
    return default_dict


def normalize_dict(probability_dict):
    total_probability = sum(probability_dict.values())
    if total_probability == 0:
        return probability_dict
    norm_dict = {
        key: value / total_probability
        for key, value in probability_dict.items()
    }
    return norm_dict


def empty_dict(country_codes):
    default_dict = {country_code: 1 for country_code in country_codes}
    return default_dict


def amplify_probs(probs, n):
    amplified_probs = {}

    for country, prob in probs.items():
        amplified_prob = prob ** (1.0 / n)
        amplified_probs[country] = amplified_prob

    return amplified_probs
