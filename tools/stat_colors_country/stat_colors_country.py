# David Bret, Paul Chambaz, Feriel Cheggour, Marion Mazaud

import argparse
import os
import csv
import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import pycountry
from tqdm import tqdm

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", help="The coordinate files")
    parser.add_argument("-j", help="The histogram json")
    return parser.parse_args()

def get_coordinates_file(string_path):
    if not string_path:
        exit(1)
    if not os.path.exists(string_path):
        print("Error, path '" + string_path + "' does not exists")
        exit(1)
    return string_path

def get_json_file(string_path):
    if not string_path:
        exit(1)
    if not os.path.exists(string_path):
        print("Error, path '" + string_path + "' does not exists")
        exit(1)
    return string_path

def read_image_histograms(json_file):
    with open(json_file, 'r') as infile:
        return json.load(infile)

def read_geolocations(coordinate_file):
    geolocations = []
    with open(coordinate_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            latitude, longitude = float(row[0]), float(row[1])
            geolocations.append((latitude, longitude))
    return  geolocations

def get_country_codes():
    country_codes = set()
    for country in pycountry.countries:
        country_codes.add(country.alpha_3)
    return country_codes

def geolocation_to_country_code(latitude, longitude, geolocator):
    try:
        location = geolocator.reverse((latitude, longitude), timeout=10)
        country_code = location.raw['address']['country_code'].upper()
        return pycountry.countries.get(alpha_2=country_code).alpha_3
    except GeocoderTimedOut:
        print(f"GeocoderTimedOut: Retrying for coordinates ({latitude}, {longitude})")
        return geolocation_to_country_code(latitude, longitude)
    except Exception as e:
        print(f"Error: {e} for coordinates ({latitude}, {longitude})")
        return None

def init_empty_histogram():
    return {
        'top': {'hue': [0] * 10, 'saturation': [0] * 10, 'value': [0] * 10},
        'middle_top': {'hue': [0] * 10, 'saturation': [0] * 10, 'value': [0] * 10},
        'middle_bottom': {'hue': [0] * 10, 'saturation': [0] * 10, 'value': [0] * 10},
        'center_bottom': {'hue': [0] * 10, 'saturation': [0] * 10, 'value': [0] * 10},
        'side_bottom': {'hue': [0] * 10, 'saturation': [0] * 10, 'value': [0] * 10}
    }

def update_country_histogram(country_histogram, image_histogram):
    for zone in country_histogram:
        for channel in country_histogram[zone]:
            for i in range(len(country_histogram[zone][channel])):
                country_histogram[zone][channel][i] += image_histogram[zone][channel][i]

def increment_country_image_count(country_image_counts, couuntry_code):
    if country_code in country_image_counts:
        country_image_counts[country_code] += 1
    else:
        country_image_counts[country_code] = 1

def average_country_histogram(country_histogram, image_count):
    for zone in country_histogram:
        for channel in country_histogram[zone]:
            for i in range(len(country_histogram[zone][channel])):
                country_histogram[zone][channel][i] /= image_count
                country_histogram[zone][channel][i] = int(country_histogram[zone][channel][i])


args = get_args()
json_file = get_coordinates_file(args.j)
coordinate_file = get_coordinates_file(args.c)

image_histograms = read_image_histograms(json_file)
geolocations = read_geolocations(coordinate_file)

geolocator = Nominatim(user_agent="gsv_histogram_analysis")
country_codes = get_country_codes()

country_histograms = {}

country_image_counts = {}
for image_filename, image_histogram in tqdm(image_histograms.items()):
    image_number = int(image_filename.split('.')[0])
    latitude, longitude = geolocations[image_number]
    country_code = geolocation_to_country_code(latitude, longitude, geolocator)

    if country_code not in country_histograms:
        country_histograms[country_code] = init_empty_histogram()

    update_country_histogram(country_histograms[country_code], image_histogram)
    increment_country_image_count(country_image_counts, country_code)

for country_code in country_codes:
    if country_code in country_histograms and country_code in country_image_counts:
        average_country_histogram(country_histograms[country_code], country_image_counts[country_code])

with open('image_histograms_country.json', 'w') as outfile:
    json.dump(country_histograms, outfile)
