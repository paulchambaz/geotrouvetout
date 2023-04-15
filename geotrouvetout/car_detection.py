import logging
from ultralytics import YOLO
from PIL import Image

def car_detection(image: Image.Image) -> dict[str, float]:
    """
    Get country from car present on image.

    @param image PIL image object.
    @return A dictionary with the country and a probability associated from the
    cars detected on the image.
    """
    logging.info("car_detection")

    car_images = detect_cars(image)

    car_brand_total: dict[str, float] = {}
    car_brand_count: dict[str, int] = {}

    for car_image in car_images:
        car_brand = detect_car_brand(car_image)

        if car_brand:
            proba = get_proba_car_country(car_brand)

            for brand, conf in proba.items():
                if brand in car_brand_total:
                    car_brand_total[brand] += conf
                    car_brand_count[brand] += 1
                else:
                    car_brand_total[brand] = conf
                    car_brand_count[brand] = 1

    car_brand_proba = {}
    for brand, total_conf in car_brand_total.items():
        car_brand_proba[brand] = (
            total_conf / car_brand_count[brand]
        )

    return car_brand_proba


def detect_cars(image: Image.Image) -> list[Image.Image]:
    """
    Uses YOLO to detect cars then return cropped images of the cars.

    @param image PIL image to be analyzed.
    @return A list of PIL image representing cars from the image.
    """
    logging.info("detect_cars")

    model = YOLO("weights/car.pt")
    model.conf = 0.25

    results = model(image)

    cropped_images = []
    for result in results:
        for box in result.boxes:
            for xyxy in box.xyxy:
                x1, y1, x2, y2 = xyxy
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cropped_image = image.crop((x1, y1, x2, y2))
                cropped_images.append(cropped_image)

    return cropped_images

def detect_car_brand(image: Image.Image) -> dict[str, float]:
    """
    Uses computer vision to classify the brand of the car from an image.

    @param image PIL image of a car.
    @return A dict containing brands of cars and the confidence of the guess.
    """
    logging.info("detect_car_brand")

    return {}

def get_proba_car_country(car_brand: dict[str, float]) -> dict[str, float]:
    """
    Uses a geodata to guess in which country we might be.

    Uses a json containing frequency of each country of car brands to
    estimate what country do we have the biggest chance of being in.

    @param car_brand Dictionary containing brands of cars and the
    confidence of the guess.
    @return A dict of country and confidence that we are in the country.
    """
    logging.info("get_proba_car_country")

    return {}
