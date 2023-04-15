"""
This modules contains function to combine different image analysis.

This module contains a set of functions for determining the most likely
countries that a given image corresponds to. It makes use of all other
geotrouvetout methods for imaga analysis and combines them to a final
probability.
"""

from collections import defaultdict
import json
import logging
import pycountry
from PIL import Image
import geotrouvetout


def get_country(image: Image.Image) -> dict[str, float]:
    """
    Get the most likely countries that a given image corresponds to.

    @param image A PIL image.
    @return A dictionary with the countries as keys and the probability of the
    image belonging to each image as values.
    """
    logging.info("get_country")

    country_codes = [c.alpha_3 for c in pycountry.countries]

    areas = geotrouvetout.get_country_areas()
    if areas:
        # TODO: the result is too biased for areas - maybe we should reduce the
        # variability and their importance
        # in general the combination method is too biased towards areas size
        # maybe we should modify areas so they are not a probability but
        # instead expressed as a percentage of the biggest area and then
        # averaged around the average area - find a function that does this
        # well - maybe its a different scale?
        area_dict = get_countries_dict(areas, country_codes)
        area_dict = normalize_dict(area_dict)
    else:
        area_dict = empty_dict(country_codes)

    color_analysis = geotrouvetout.get_color_analysis(image)
    if color_analysis:
        color_analysis = amplify_probs(color_analysis, 2)
        color_dict = get_countries_dict(color_analysis, country_codes)
    else:
        color_dict = empty_dict(country_codes)

    languages = geotrouvetout.get_languages(image)
    if languages:
        language_dict = get_countries_dict(
            get_country_languages(languages, "stats/country_metadata.json"),
            country_codes,
        )
    else:
        language_dict = empty_dict(country_codes)

    evidence = {
        key: (area_dict[key] * color_dict[key] * language_dict[key])
        for key in country_codes
    }
    total_evidence = sum(evidence.values())

    combined_dict = {
        key: bayesian_update(
            area_dict[key],
            color_dict[key] * language_dict[key],
            total_evidence,
        )
        for key in country_codes
    }

    # old method
    # combined_dict = {
    #     key: (area_dict[key] * color_dict[key] * language_dict[key])
    #     for key in country_codes
    # }

    return combined_dict


def bayesian_update(prior: float, likelihood: float, evidence: float) -> float:
    """
    Update the prior probability with new evidence using bayes't theorem.

    @param prior The prior probability of the event.
    @param likelihood The likelihood of the event given the evidence.
    @param evidence The evidence of the event.
    @return The updated probability of the event.
    """
    return prior * likelihood / evidence


def get_country_languages(languages: dict[str, float],
                          country_metadata_file: str) -> dict[str, float]:
    """
    Calculate the average probability of each country from languages.

    Calculates the average probability of each country in a given language
    probability dictionary.

    @param languages A dictionary of language probabilities.
    @param country_metadata_file The path to a JSON file containing each
    countries spoken language metadata.

    @return A dictionary of country codes with their corresponding average
    probabilities.
    """
    with open(country_metadata_file, "r", encoding="utf-8") as file:
        country_metadata = json.load(file)
    country_prob: dict[str, float] = defaultdict(float)
    for lang, prob in languages.items():
        lang_countries = [
            key
            for key, value in country_metadata.items()
            if lang in value["languages"]
        ]
        for country in lang_countries:
            country_prob[country] += prob

    num_langs = len(languages)
    avg_country_prob = {
        key: value / num_langs for key, value in country_prob.items()
    }
    return avg_country_prob


def get_countries_dict(input_dict: dict[str, float],
                       country_codes: list[str]) -> dict[str, float]:
    """
    Create a dictionary of country code - probability.

    Creates a dictionary of country codes with default values based on an
    input dictionary.

    @param input_dict The input dictionary to create the default dictionary
    from.
    @param country_codes A list of country codes to use as the keys in the
    default dictionary.

    @return A dictionary of country codes with default values based on the
    input dictionary.
    """
    min_value = min(value for value in input_dict.values() if value > 0)
    default_dict = {
        country_code: min_value / 2 for country_code in country_codes
    }
    default_dict.update(input_dict)
    return default_dict


def normalize_dict(probability_dict: dict[str, float]) -> dict[str, float]:
    """
    Normalize the values of a probability dictionary so that they add up to 1.

    @param probability_dict The input dictionary of probabilities to be
    normalized.

    @return A new dictionary with the same keys as the input dictionary, but
    with the values normalized.
    """
    total_probability = sum(probability_dict.values())
    if total_probability == 0:
        return probability_dict
    norm_dict = {
        key: value / total_probability
        for key, value in probability_dict.items()
    }
    return norm_dict


def empty_dict(country_codes: list[str]) -> dict[str, float]:
    """
    Create a dictionary with default values of 1 for each country code.

    @param country_codes A list of country codes.

    @return A dictionary with each country code as a key and a default value
    of 1 for each key.
    """
    default_dict = {country_code: 1.0 for country_code in country_codes}
    return default_dict


def amplify_probs(probs: dict[str, float], factor: int) -> dict[str, float]:
    """
    Amplifies the value of a given probability.

    Amplifies the values of a probability dictionary by taking the nth
    root of each value.

    @param probs The input dictionary of probabilities to be amplified.
    @param n An integer representing the degree of amplification.

    @return A new dictionary with the same keys as the input dictionary, but
    with the values amplified.
    """
    amplified_probs = {}

    for country, prob in probs.items():
        amplified_prob = prob ** (1.0 / factor)
        amplified_probs[country] = amplified_prob

    return amplified_probs
