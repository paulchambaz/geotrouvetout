"""! @brief Command line interface for geotrouvetout."""

import sys
import argparse
import logging
import pathlib
import uvicorn
import coloredlogs
import geotrouvetout
import numpy
import matplotlib.image as mimg
import pycountry
from PIL import Image
import cv2

# argument parsing


def main():
    parser = argparse.ArgumentParser(
        description="Get information about an image geolocation"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
        help="Show the version number and exit",
    )

    parser.add_argument("-i", "--image", type=str, help="Path to the image")

    parser.add_argument(
        "-d", "--daemon", action="store_true", help="Run program as daemon"
    )

    parser.add_argument(
        "-v", action="count", default=0, help="Increase verbosity level"
    )

    args = parser.parse_args()

    if args.daemon and args.image:
        parser.error("Only one of -d or -i can be used at a time.")
        sys.exit(0)
    elif not args.daemon and not args.image:
        parser.print_usage()
        sys.exit(0)

    log_level = "WARNING"
    if args.v == 1:
        log_level = "INFO"
    elif args.v >= 2:
        log_level = "DEBUG"

    # initiate subsystems
    # TODO - use environement variables to pass debug level
    coloredlogs.install(
        level=log_level,
        fmt="%(levelname)s: %(asctime)s %(message)s",
        datefmt="%H:%M:%S",
        colors={
            "DEBUG": "blue",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red",
        },
    )

    # start cli image analysis
    if args.image:
        image_file = pathlib.Path(args.image)
        if not image_file.is_file():
            parser.print_usage()
            sys.exit(1)

        if image_file.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            parser.print_usage()
            sys.exit(1)

        image = Image.open(image_file)
        country_probs = geotrouvetout.get_country(image)

        sorted_country_probs = sorted(
            country_probs.items(), key=lambda x: x[1], reverse=True
        )

        for country, prob in sorted_country_probs:
            percent_prob = int(prob * 100)
            if not percent_prob == 0:
                country_name = pycountry.countries.get(alpha_3=country).name
                print(f"{country_name}: {percent_prob}%")

    # start daemon
    elif args.daemon:
        uvicorn.run("rest_api.__main__:app", host="0.0.0.0", port=8000)
