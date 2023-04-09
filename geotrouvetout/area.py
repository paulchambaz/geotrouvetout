"""
This module contains utility functions for getting country area information.

The module includes functions to load a dictionary with country codes as keys
and their respective areas as values.
"""

import logging
import csv


def get_country_areas() -> dict[str, float]:
    """
    Load a dictionary that contains area data for each country.

    @return A dictionary with 3 letter country code as keys and their
    respective areas as values.
    @throw IOError If the CSV file with the area data cannot be found or
    opened.
    @throw ValueError If the CSV file has invalid data for the area value.
    """
    logging.info("load_country_area")
    country_areas = {}
    with open("stats/area.csv", "r", encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        for row in csvreader:
            country_code = row[0]
            area = float(row[1])
            country_areas[country_code] = area

    return country_areas
