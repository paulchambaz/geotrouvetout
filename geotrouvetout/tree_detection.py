import logging
from ultralytics import YOLO
from PIL import Image

def tree_detection(image: Image.Image) -> dict[str, float]:
    """
    Get country from tree present on image.

    @param image PIL image object.
    @return A dictionary with the country and a probability associated from the
    trees detected on the image.
    """
    logging.info("tree_detection")

    tree_images = detect_trees(image)

    tree_specie_total: dict[str, float] = {}
    tree_specie_count: dict[str, int] = {}

    for tree_image in tree_images:
        tree_specie = detect_tree_specie(tree_image)

        if tree_specie:
            proba = get_proba_tree_country(tree_specie)

            for specie, conf in proba.items():
                if specie in tree_specie_total:
                    tree_specie_total[specie] += conf
                    tree_specie_count[specie] += 1
                else:
                    tree_specie_total[specie] = conf
                    tree_specie_count[specie] = 1

    tree_specie_proba = {}
    for specie, total_conf in tree_specie_total.items():
        tree_specie_proba[specie] = (
            total_conf / tree_specie_count[specie]
        )

    return tree_specie_proba


def detect_trees(image: Image.Image) -> list[Image.Image]:
    """
    Uses YOLO to detect trees then return cropped images of the trees.

    @param image PIL image to be analyzed.
    @return A list of PIL image representing trees from the image.
    """
    logging.info("detect_trees")

    model = YOLO("weights/tree.pt")
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

def detect_tree_specie(image: Image.Image) -> dict[str, float]:
    """
    Uses computer vision to classify the specie of the tree from an image.

    @param image PIL image of a tree.
    @return A dict containing species of trees and the confidence of the guess.
    """
    logging.info("detect_tree_specie")

    return {}

def get_proba_tree_country(tree_specie: dict[str, float]) -> dict[str, float]:
    """
    Uses a geodata to guess in which country we might be.

    Uses a json containing frequency of each country of tree species to
    estimate what country do we have the biggest chance of being in.

    @param tree_specie Dictionary containing species of trees and the
    confidence of the guess.
    @return A dict of country and confidence that we are in the country.
    """
    logging.info("get_proba_tree_country")

    return {}
