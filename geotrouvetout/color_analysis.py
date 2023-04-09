"""
Computes promitiy to countries color profile.

This module provides functions for analyzing the color profile of images and
comparing them to country-sepecific profiles.

The module includes functions to compute histograms of hue, saturation, and
value for a given image divided into multiple zones, load country-specific
histograms from a JSON file, compute the chi-square distance between two
histograms, and compare the color histograms of an input image with the
histograms of each country in the JSON file to determine the best match.

The image is cut into five zones: sky, upper-building/trees,
lower-building/grass, road, and dirt/grass. Each zone is divided into channels:
hue, saturation, and value. A 10-bin histogram is created for each channel in
each zone.
"""

import json
import logging
from PIL import Image
import numpy as np
from skimage import color


def get_color_analysis(image: Image.Image) -> dict[str, float]:
    """
    Compute color analysis for an image.

    Compute the color analysis of an input image and compare it to a database
    of country-specific color profiles.

    @param image The imput image to be analysed.
    @return A dictionary with country codes as keys and their scores as values.
    """
    logging.info("get_color_analysis")

    # compute histograms for the given image
    zones = create_zone_images(image)
    image_histograms = {}
    for zone_name, zone_image in zones.items():
        histograms = create_histograms(zone_image)
        image_histograms[zone_name] = histograms

    # load the country histograms dictionary from JSON file
    countries_histograms = load_country_histograms(
        "stats/image_histograms_country.json"
    )

    # compare the image histograms with the country histograms
    result = {}
    for country_code, country_histograms in countries_histograms.items():
        distance = compare_histograms(image_histograms, country_histograms)
        result[country_code] = 1.0 - distance

    return result


def load_country_histograms(
    json_file: str,
) -> dict[str, dict[str, dict[str, list[int]]]]:
    """
    Load a dictionary of country-specific histograms from a JSON file.

    @param json_file THe path to the JSON file containing the JSON file.
    @return A dictionary with country codes as keys and their respective
    histograms as values.
    """
    logging.info("load_country_histograms")
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"Invalid data format in {json_file}: expected a \
        dictionary got {type(data)}"
        )

    for country, zones in data.items():
        if not isinstance(country, str):
            raise ValueError(
                f"Invalid data format in {json_file}: expected a \
            string got {type(country)}"
            )
        if not isinstance(zones, dict):
            raise ValueError(
                f"Invalid data format in {json_file}: expected a \
            dictionary got {type(zones)}"
            )

        for zone, channels in zones.items():
            if not isinstance(country, str):
                raise ValueError(
                    f"Invalid data format in {json_file}: \
                expected a string got {type(zone)}"
                )
            if not isinstance(channels, dict):
                raise ValueError(
                    f"Invalid data format in {json_file}: \
                expected a dictionary got {type(channels)}"
                )

            for channel, histogram in channels.items():
                if not isinstance(channel, str):
                    raise ValueError(
                        f"Invalid data format in {json_file}: \
                    expected a string got {type(channel)}"
                    )
                if not isinstance(histogram, list):
                    raise ValueError(
                        f"Invalid data format in {json_file}: \
                    expected a string got {type(histogram)}"
                    )

                for element in histogram:
                    if not isinstance(element, int):
                        raise ValueError(
                            f"Invalid data format in {json_file}: \
                        expected a integer got {type(bin)}"
                        )
    return data


def create_zone_images(image: Image.Image) -> dict[str, Image.Image]:
    """
    Create zone images for a given image.

    Creates five zones by dividing the input image vertically into four
    quarters and the bottom quarter horizontally into a middle third and two
    side thirds.

    @param image The input image.
    @return A dictionary with five zones where the keys are zone names and the
    values are corresponding zone images.
    """
    logging.info("create_zone_images")
    width, height = image.size
    quarter_height = height // 4
    middle_third_width = width // 3

    # crop the image into five zones
    top_quarter = image.crop((0, 0, width, quarter_height))
    middle_top_quarter = image.crop(
        (0, quarter_height, width, 2 * quarter_height)
    )
    middle_bottom_quarter = image.crop(
        (0, 2 * quarter_height, width, 3 * quarter_height)
    )
    center_bottom_quarter = image.crop(
        (
            middle_third_width,
            3 * quarter_height,
            2 * middle_third_width,
            height,
        )
    )
    left_bottom_quarter = image.crop(
        (0, 3 * quarter_height, middle_third_width, height)
    )
    right_bottom_quarter = image.crop(
        (2 * middle_third_width, 3 * quarter_height, width, height)
    )

    # paste the left and right thirds of the side bottom zone into a single
    # image
    side_bottom_quarter = Image.new(
        "RGB", (2 * middle_third_width, height - 3 * quarter_height)
    )
    side_bottom_quarter.paste(left_bottom_quarter, (0, 0))
    side_bottom_quarter.paste(right_bottom_quarter, (middle_third_width, 0))

    # create a dictionary with the zones names as keys and the corresponding
    # zone images as values
    zones = {
        "top": top_quarter,
        "middle_top": middle_top_quarter,
        "middle_bottom": middle_bottom_quarter,
        "center_bottom": center_bottom_quarter,
        "side_bottom": side_bottom_quarter,
    }

    return zones


def create_histograms(
    image: Image.Image, bins: int = 10
) -> dict[str, dict[str, list[int]]]:
    """
    Create histograms for an image, given the number of bins.

    @param image The image to create histograms for.
    @param bins The number of bins to use for the histograms.
    @return A dictionary with the hue, saturation and value histograms for the
    image.
    """
    logging.info("create_histograms")

    # conver the image to a numpy array and then to HSV color space
    np_image = np.array(image)
    hsv_image = color.rgb2hsv(np_image)

    # creates histograms for the hue saturation and value channels
    hue_histogram, _ = np.histogram(
        hsv_image[:, :, 0], bins=bins, range=(0, 1)
    )
    saturation_histogram, _ = np.histogram(
        hsv_image[:, :, 1], bins=bins, range=(0, 1)
    )
    value_histogram, _ = np.histogram(
        hsv_image[:, :, 2], bins=bins, range=(0, 1)
    )

    # creates a dictionary containing the histograms as lists
    histograms = {
        "hue": hue_histogram.tolist(),
        "saturation": saturation_histogram.tolist(),
        "value": value_histogram.tolist(),
    }

    return histograms


def compare_histograms(
    image: Image.Image, country: dict[str, dict[str, list[int]]]
) -> float:
    """
    Compare the distance between the histograms of an image and a country.

    @param image The image to compare.
    @param country A dict containing the histograms for HSV of the five zones
    for each country
    """
    weights = get_histogram_distance_weights()

    # compute total weights
    total_weights = 0.0
    for zone, channel_weights in weights.items():
        for channel_weight in channel_weights.values():
            total_weights += channel_weight

    # compute distance
    distance = 0.0
    for zone, channel_weights in weights.items():
        for channel, weight in channel_weights.items():
            distance += weight * get_dist(image, country, zone, channel)

    return distance / total_weights


def get_histogram_distance_weights() -> dict[str, dict[str, float]]:
    """
    Return weights for histogram comparison.

    Returns a dictionary containing the weights for different zones and
    channels used in computing the distance between two histograms.

    @return A dictionary with keys and values for the weights for each zone of
    the image.
    """
    logging.info("get_histogram_distance_weights")

    # define weights for different zones
    top_weight = 0.2
    middle_top_weight = 0.5
    middle_bottom_weight = 1.0
    center_bottom_weight = 2.0
    side_bottom_weight = 1.0

    # define weights for different channels
    hue_weight = 4.0
    saturation_weight = 2.0
    value_weight = 1.0

    return {
        "top": {
            "hue": top_weight * hue_weight,
            "saturation": top_weight * saturation_weight,
            "value": top_weight * value_weight,
        },
        "middle_top": {
            "hue": middle_top_weight * hue_weight,
            "saturation": middle_top_weight * saturation_weight,
            "value": middle_top_weight * value_weight,
        },
        "middle_bottom": {
            "hue": middle_bottom_weight * hue_weight,
            "saturation": middle_bottom_weight * saturation_weight,
            "value": middle_bottom_weight * value_weight,
        },
        "center_bottom": {
            "hue": center_bottom_weight * hue_weight,
            "saturation": center_bottom_weight * saturation_weight,
            "value": center_bottom_weight * value_weight,
        },
        "side_bottom": {
            "hue": side_bottom_weight * hue_weight,
            "saturation": side_bottom_weight * saturation_weight,
            "value": side_bottom_weight * value_weight,
        },
    }


def chi_square_distance(hist1: list[int], hist2: list[int]) -> float:
    """
    Calculate the chi-square distance between two histograms.

    @param hist1 The first histogram to compare.
    @param hist2 The second histogram to compare.
    @return The chi-square distance between the two histograms.
    """
    logging.info("chi_square_distance")

    # normalize the histograms
    hist1_normalized = [value / sum(hist1) for value in hist1]
    hist2_normalized = [value / sum(hist2) for value in hist2]

    # calculate the distance using chi-square formula
    distance = 0.0
    for value1, value2 in zip(hist1_normalized, hist2_normalized):
        if value1 + value2 != 0:
            distance += ((value1 - value2) ** 2) / (value1 + value2)
    return distance / 2


def get_dist(
    image_histograms: dict[str, dict[str, list[int]]],
    country_histograms: dict[str, dict[str, list[int]]],
    zone: str,
    channel: str,
) -> float:
    """
    Compute distance between two histograms.

    Computes the chi-square distance between two histograms of a specific
    channel and zone.

    @param image_histograms A dictionary containing the image histograms for
    each zone and channel.
    @param country_histograms A dictionary containg the country histograms for
    each zone and channel.
    @param zone A string specifying the zone for which to calculate the
    distance.
    @param channel A string speciying the channel for which to calculate the
    distance.
    """
    logging.info("get_dist")
    return chi_square_distance(
        image_histograms[zone][channel], country_histograms[zone][channel]
    )
