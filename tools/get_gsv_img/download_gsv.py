# David Bret, Paul Chambaz, Feriel Cheggour, Marion Mazaud

import typing
import argparse
import io
import os
import csv
import random
import requests
import json
from shapely.geometry import Point, shape
from shapely.errors import TopologicalError
from tqdm import tqdm

def get_args() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-n", help="The number of images to get")
    parser.add_argument("-o", help="The location of the output folder")
    parser.add_argument("-k", help="The api key of Google StreetView api")
    return parser.parse_args()

def get_number_images(string_number_images: str) -> int:
    if not string_number_images:
        exit(1)
    if not string_number_images.isdigit():
        print("Error, number of images must be a number")
        exit(1)
    number_images: int = int(string_number_images)
    if number_images < 1 or number_images > 10000:
        print("Error, number of images must be between 1 and 10000")
        exit(1)
    return number_images

def get_path(string_path: str) -> str:
    if not string_path:
        exit(1)
    if not os.path.exists(string_path):
        print("Error, path '" + string_path + "' does not exists")
        exit(1)
    return string_path

def get_api_key(string_key: str) -> str:
    return string_key

def get_country_borders(file_path):
    with open(file_path, mode='r') as file:
        return json.load(file)

def read_area_csv(file_path):
    area_dict = {}
    with open(file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            area_dict[row['country_code']] = float(row['area'])
    return area_dict

def calculate_total_area(countries):
    return sum(area_dict.values())

def pick_random_country(countries, total_area):
    rand_area = random.uniform(0, total_area)
    current_area = 0
    for country in countries:
        country_code = country['properties']['ISO_A3']
        current_area += area_dict.get(country_code, 0)
        if current_area >= rand_area:
            return country
    return None

def get_bounding_box(country):
    try:
        country_shape = shape(country.get('geometry'))
        return country_shape.bounds
    except Exception:
        return 0, 0, 0, 0

def pick_random_point(country):
    min_lng, min_lat, max_lng, max_lat = get_bounding_box(country)
    return random.uniform(min_lat, max_lat), random.uniform(min_lng, max_lng)

def is_point_within_country(point, country):
    lat, lng = point
    point = Point(lng, lat)
    try:
        return point.within(shape(country['geometry']))
    except Exception:
        return False


def pick_random_lat_lng(countries, area_dict, total_area):
    while True:
        selected_country = pick_random_country(countries, total_area)
        random_point = pick_random_point(selected_country)
        if is_point_within_country(random_point, selected_country):
            return random_point

def get_street_view_image(lat, lng, api_key, max_radius=65536):
    def request_metadata(lat, lng, radius, api_key):
        url = f"https://maps.googleapis.com/maps/api/streetview/metadata?location={lat},{lng}&radius={radius}&key={api_key}"
        return requests.get(url)

    def request_image(lat, lng, api_key, size="640x640"):
        url = f"https://maps.googleapis.com/maps/api/streetview?size={size}&fov=120&source=outdoor&return_error_code=true&location={actual_lat},{actual_lng}&key={api_key}"
        return requests.get(url)

    radius = 1024
    metadata_response = request_metadata(lat, lng, radius, api_key)

    # we try to find on that works until we reach the maximum radius allowed
    while metadata_response.status_code == 200 and metadata_response.json()['status'] == 'ZERO_RESULTS' and radius <= max_radius:
        radius *= 2
        metadata_response = request_metadata(lat, lng, radius, api_key)

    if not (metadata_response.status_code == 200 and metadata_response.json()['status'] != 'ZERO_RESULTS'):
        return None, None

    metadata = metadata_response.json()
    if 'location' not in metadata:
        return None, None

    actual_lat, actual_lng = metadata['location']['lat'], metadata['location']['lng']
    response = request_image(actual_lat, actual_lng, api_key)

    if not response.status_code == 200:
        return None, None

    image = response.content
    return image, (actual_lat, actual_lng)

def count_csv_rows(filename):
    with open(filename, 'r', newline='') as csvfile:
        return sum(1 for row in csv.reader(csvfile))

# get the arguments
args = get_args()
number_images: int = get_number_images(args.n)
path: str = get_path(args.o)
api_key: str = get_api_key(args.k)
url: str = "https//maps.googleapis.com/maps/api/streetview"

csv_filename = f"{path}/coords.csv"

if not os.path.exists(csv_filename):
    with open(csv_filename, 'w', newline='') as csvfile:
        pass

current_index = count_csv_rows(csv_filename)

country_borders = get_country_borders('countries.geojson')
countries = country_borders['features']
area_dict = read_area_csv('area.csv')
total_area = calculate_total_area(area_dict)

with open(csv_filename, 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)

    for i in tqdm(range(current_index, current_index + number_images)):
        success = False

        while not success:
            lat, lng = pick_random_lat_lng(countries, area_dict, total_area)
            image, lat_lng = get_street_view_image(lat, lng, api_key)

            if image is not None:
                with open(f"{path}/{i}.png", "wb") as img_file:
                    img_file.write(image)
                csv_writer.writerow([lat_lng[0], lat_lng[1]])
                success = True
