"""
This file contains functions for detecting languages in an image that contain
road signs
"""

import logging
import numpy as np
import numpy.typing as npt
import math
import tkinter
import matplotlib.pyplot as mplt
import cv2
import pytesseract
from langdetect import detect_langs
from collections import defaultdict
import pycountry
from PIL import Image
import pandas as pd
from ultralytics import YOLO


def get_languages(image: Image) -> dict[str, float]:
    """
    Detect languages in an image
    @param image The image to detect the languages in
    @return list of tuple that contain a language code and the confidence level
    """
    logging.info("get_languages")
    logging.getLogger("yolov8").setLevel(logging.WARNING)

    # get the images from yolo
    detected_signs = detect_road_signs(image)

    detected_languages_total_conf = {}
    detected_languages_count = {}

    logging.info(
        f"{len(detected_signs)} images of road signs detected, starting analysis"
    )

    for sign_image in detected_signs:
        try:
            # process the image
            processed_image = process_image(sign_image)

            # detect text and confidences in the image
            text_and_confidences = detect_text(processed_image)

            # log the text detected
            for text, conf in text_and_confidences:
                logging.info(f"Text detected : {text}, {int(conf)}%")

            # detect languages in the text and confidence
            language_detected = detect_languages(text_and_confidences)

            # combine the detected languages and compute the total confidence and count
            for lang, conf in language_detected.items():
                if lang in detected_languages_total_conf:
                    detected_languages_total_conf[lang] += conf
                    detected_languages_count[lang] += 1
                else:
                    detected_languages_total_conf[lang] = conf
                    detected_languages_count[lang] = 1
        except ValueError as e:
            logging.info(e)

    detected_languages_avg_conf = {}
    for lang, total_conf in detected_languages_total_conf.items():
        detected_languages_avg_conf[lang] = (
            total_conf / detected_languages_count[lang]
        )

    return detected_languages_avg_conf


def detect_road_signs(image: Image) -> list[npt.NDArray[np.uint8]]:
    """
    Detect road signs in an image using YOLO and return the cropped images
    @param image PIL Image
    @return list of cropped road sign np images detected in the image
    """
    yolo_logger = logging.getLogger("yolov8")
    yolo_logger.setLevel(logging.ERROR)

    model = YOLO("weights/traffic_sign.pt")

    model.conf = 0.25
    model.iou = 0.45
    model.agnostic = False
    model.multi_label = False
    model.max_det = 1000

    results = model(image)

    cropped_images = []
    for result in results:
        for box in result.boxes:
            for xyxy in box.xyxy:
                x1, y1, x2, y2 = xyxy
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cropped_image = image.crop((x1, y1, x2, y2))
                cropped_images.append(np.array(cropped_image))

    return cropped_images


def process_image(image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
    """
    Preprocess image for text detection by cleaning and enhancing it
    @param image file path
    @return preprocessed image file paths
    """
    logging.info("preprocess_images")

    logging.debug("Converting to grayscale")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = gray.astype(np.float32) / 255.0
    min_val, max_val = cv2.minMaxLoc(gray)[:2]
    stretched_image = cv2.normalize(
        gray, None, 0.0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F
    )

    logging.debug("Applying blur")
    blurred = cv2.GaussianBlur(stretched_image, (5, 5), 1.4)

    logging.debug("Computing gradient")
    gx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
    gradient = cv2.magnitude(gx, gy)

    logging.debug("Getting inverted binary")
    _, binary_image = cv2.threshold(gradient, 0.1, 1.0, cv2.THRESH_BINARY)

    inverted_image = np.zeros_like(binary_image)
    inverted_image = 1 - binary_image

    logging.debug("Getting connected component")
    inverted_image = (inverted_image * 255).astype("uint8")
    _, labels, stats, _ = cv2.connectedComponentsWithStats(inverted_image)

    stats = [(i,) + tuple(stats[i]) for i in range(len(stats))]

    stats = sorted(
        stats[1:], key=lambda x: x[cv2.CC_STAT_AREA + 1], reverse=True
    )

    largest_area = stats[0][cv2.CC_STAT_AREA + 1]

    logging.debug("Finding all large components to create component image")
    component_image = np.zeros_like(inverted_image)
    for stat in stats:
        label = stat[0]
        area = stat[cv2.CC_STAT_AREA + 1]
        if area >= largest_area * 0.5:
            component_image[labels == label] = 255

    logging.debug("Filling small holes")
    kernel = np.ones((5, 5), np.uint8)
    filled = cv2.morphologyEx(component_image, cv2.MORPH_CLOSE, kernel)

    filled = fill_holes(filled)

    logging.debug("Finding contour of filled shape to correct pespective")
    contours, _ = cv2.findContours(
        filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    largest_countour = max(contours, key=cv2.contourArea)

    logging.debug("Approximating shape to polygon")

    approx_quad = None
    max_iterations = 10
    iteration = 0
    while (
        approx_quad is None or len(approx_quad) != 4
    ) and iteration < max_iterations:
        epsilon = (
            (iteration + 1) * 0.01 * cv2.arcLength(largest_countour, True)
        )
        approx_quad = cv2.approxPolyDP(largest_countour, epsilon, True)
        iteration += 1

    if approx_quad is None or len(approx_quad) != 4:
        raise ValueError("Failed to approximate polygon with 4 vertices.")

    logging.debug("Correcting perspective")
    src_pts = approx_quad.reshape(4, 2).astype(np.float32)

    src_pts_ordered = np.zeros_like(src_pts)
    s = src_pts.sum(axis=1)
    src_pts_ordered[0] = src_pts[np.argmin(s)]
    src_pts_ordered[2] = src_pts[np.argmax(s)]
    d = np.diff(src_pts, axis=1)
    src_pts_ordered[1] = src_pts[np.argmin(d)]
    src_pts_ordered[3] = src_pts[np.argmax(d)]

    side_lengths = [
        np.linalg.norm(src_pts_ordered[i] - src_pts_ordered[i - 1])
        for i in range(4)
    ]

    output_height = int(round((side_lengths[0] + side_lengths[2]) / 2))
    output_width = int(round((side_lengths[1] + side_lengths[3]) / 2))

    # output_width, output_height = 500, 100
    dst_pts = np.array(
        [
            [0, 0],
            [output_width - 1, 0],
            [output_width - 1, output_height - 1],
            [0, output_height],
        ],
        dtype=np.float32,
    )

    perspective_matrix = cv2.getPerspectiveTransform(src_pts_ordered, dst_pts)
    warped_image = cv2.warpPerspective(
        stretched_image, perspective_matrix, (output_width, output_height)
    )
    warped_background = cv2.warpPerspective(
        component_image, perspective_matrix, (output_width, output_height)
    )

    warped_image = warped_image
    min_val, max_val = cv2.minMaxLoc(warped_image)[:2]
    warped_stretched_image = cv2.normalize(
        warped_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U
    )

    logging.debug("Adding blur")

    text = cv2.GaussianBlur(warped_stretched_image, (3, 3), 1)
    text = extract_text(text, warped_background)

    return text


def detect_text(image: npt.NDArray[np.uint8]) -> list[tuple[str, int]]:
    """
    Detect text in an image
    @param Path to the image file
    @return Detected text as a string
    """
    logging.info("detect_text")

    data = pytesseract.image_to_data(
        image, output_type=pytesseract.Output.DICT
    )

    text_and_confidences = []
    for text, conf in zip(data["text"], data["conf"]):
        if int(conf) > 0 and text.strip():
            text_and_confidences.append((text, int(conf)))
    return text_and_confidences


def detect_languages(text_and_confidences: list[str]) -> dict[str, float]:
    """
    Detect languages list of texts
    @param text_and_confidences list of texts to detect language from
    @return a list of tuple that contain a country code and a confidence level
    """
    logging.info("detect_languages")

    language_confidences = defaultdict(int)

    min_text_length = 3

    for text, conf in text_and_confidences:
        if len(text) < min_text_length:
            logging.info(
                f"Skipping '{text}' as its length is below the minimum threshold"
            )
            continue
        try:
            lang_detection = detect_langs(text)
            for lang in lang_detection:
                language_confidences[lang.lang] += lang.prob * conf * len(text)
        except Exception as e:
            logging.info(f"Skipping '{text}' as it caused lang_detect to fail")

    total_weight = sum(language_confidences.values())

    if total_weight == 0:
        return {}

    for lang in language_confidences:
        language_confidences[lang] /= total_weight

    return language_confidences


def extract_text(image, mask):
    """
    Extract text from an image using a mask of the background
    @param image Grayscale input image containing the text
    @param Binary mask where 255 indates background pixel
    @return Binary image with extracted text, where 0 indicates text and 255
    indicates background
    """
    mean = 0
    total = 0
    for j in range(image.shape[0]):
        for i in range(image.shape[1]):
            if mask[j, i] != 255:
                continue
            mean = mean + image[j, i]
            total = total + 1

    mean = int(np.rint(mean / total))

    binary = np.zeros_like(image)
    for j in range(image.shape[0]):
        for i in range(image.shape[1]):
            if mask[j, i] == 255:
                continue
            if abs(image[j, i] - mean) > 50:
                binary[j, i] = 255

    binary = 255 - binary

    kernel = np.ones((3, 3), np.uint8)
    closed_image = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    return closed_image


def fill_holes(image):
    """Fills holes in a binary image
    @param image The binary image to process
    @return The image with filled holes
    """
    filled = np.zeros_like(image)
    # Fill holes horizontally
    for row in range(image.shape[0]):
        first_white = np.argmax(image[row, :] == 255)
        last_white = image.shape[1] - np.argmax(image[row, ::-1] == 255) - 1
        if (
            first_white < last_white
            and image[row, first_white] == 255
            and image[row, last_white] == 255
        ):
            filled[row, first_white:last_white] = 255

    # Fill holes vertically
    for col in range(image.shape[1]):
        first_white = np.argmax(image[:, col] == 255)
        last_white = image.shape[0] - np.argmax(image[::-1, col] == 255) - 1
        if (
            first_white < last_white
            and image[first_white, col] == 255
            and image[last_white, col] == 255
        ):
            filled[first_white:last_white, col] = 255
    return filled
