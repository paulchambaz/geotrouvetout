# David Bret, Paul Chambaz, Feriel Cheggour, Marion Mazaud

import argparse
import os
import json
from PIL import Image
from tqdm import tqdm
import numpy as np
from skimage import color

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", help="The directory to analyze")
    return parser.parse_args()

def get_directory(string_path):
    if not string_path:
        exit(1)
    if not os.path.exists(string_path):
        print("Error, path '" + string_path + "' does not exists")
        exit(1)
    return string_path

def divide_image_into_zones(image):
    width, height = image.size
    quarter_height = height // 4
    middle_third_width = width // 3

    top_quarter = image.crop((0, 0, width, quarter_height))
    middle_top_quarter = image.crop((0, quarter_height, width, 2 * quarter_height))
    middle_bottom_quarter = image.crop((0, 2 * quarter_height, width, 3 * quarter_height))
    center_bottom_quarter = image.crop((middle_third_width, 3 * quarter_height, 2 * middle_third_width, height))
    left_bottom_quarter = image.crop((0, 3 * quarter_height, middle_third_width, height))
    right_bottom_quarter = image.crop((2 * middle_third_width, 3 * quarter_height, width, height))

    side_bottom_quarter = Image.new('RGB', (2 * middle_third_width, height - 3 * quarter_height))
    side_bottom_quarter.paste(left_bottom_quarter, (0, 0))
    side_bottom_quarter.paste(right_bottom_quarter, (middle_third_width, 0))

    zones = {
        'top': top_quarter,
        'middle_top': middle_top_quarter,
        'middle_bottom': middle_bottom_quarter,
        'center_bottom': center_bottom_quarter,
        'side_bottom': side_bottom_quarter
    }

    return zones

def create_hsv_histograms(image, bins=10):
    np_image = np.array(image)
    hsv_image = color.rgb2hsv(np_image)
    hue_histogram, _ = np.histogram(hsv_image[:, :, 0], bins=bins, range=(0, 1))
    saturation_histogram, _ = np.histogram(hsv_image[:, :, 1], bins=bins, range=(0, 1))
    value_histogram, _ = np.histogram(hsv_image[:, :, 2], bins=bins, range=(0, 1))

    histograms = {
        'hue': hue_histogram.tolist(),
        'saturation': saturation_histogram.tolist(),
        'value': value_histogram.tolist()
    }
    
    return histograms

def sort_numeric(file):
    return int(file.split('.')[0])

args = get_args()
directory = get_directory(args.d)

image_data = {}

files = [file for file in os.listdir(directory) if file.endswith('.png')]
sorted_files = sorted(files, key=sort_numeric)

for file in tqdm(sorted_files):
    image_path = os.path.join(directory, file)
    image = Image.open(image_path)
    zones = divide_image_into_zones(image)
    zone_histograms = {}
    for zone_name, zone_image in zones.items():
        histograms = create_hsv_histograms(zone_image)
        zone_histograms[zone_name] = histograms
    image_data[file] = zone_histograms

with open('image_histograms.json', 'w') as outfile:
    json.dump(image_data, outfile)
