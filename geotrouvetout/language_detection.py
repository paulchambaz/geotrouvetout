"""
Module.

Module.
"""

import logging
from collections import defaultdict
import numpy as np
import numpy.typing as npt
import cv2
import pytesseract
from langdetect import detect_langs
from PIL import Image
from ultralytics import YOLO
from typing import Any


def get_languages(image: Image.Image) -> dict[str, float]:
    """
    Get information about language present in an image.

    Returns a dictionary with the detected languages in the given image and
    their average confidence.

    @param image PIL Image object representing the image to be analyzed
    @return A dictionary with the detected languages and their average
    confidence in the image. They keys are 2 letter language codes and the
    values are between 0 and 1.
    """
    logging.info("get_languages")

    # detect road signs in the image using YOLO
    detected_signs = detect_road_signs(image)

    # initialize dictionaries to keep track of total confidence of count for
    # each detected language
    detected_languages_total_conf: dict[str, float] = {}
    detected_languages_count: dict[str, int] = {}

    logging.info(
        f"{len(detected_signs)} images of road signs detected, \
starting analysis"
    )

    # iterate through each detected sign and analyze the text in each
    for sign_image in detected_signs:
        try:
            # process the sign image to prepare it for text detection
            processed_image = process_image(sign_image)

            # detect text and confidences in the processed image
            text_and_confidences = detect_text(processed_image)

            # log the text detected for debugging purposes
            for text, conf in text_and_confidences.items():
                logging.info(f"Text detected : {text}, {int(conf)}%")

            # detect the languages in the text and their respective confidences
            language_detected = detect_languages(text_and_confidences)

            # combine the detected languages and compute the toatl confidence
            # and count for each
            for lang, conf in language_detected.items():
                if lang in detected_languages_total_conf:
                    detected_languages_total_conf[lang] += conf
                    detected_languages_count[lang] += 1
                else:
                    detected_languages_total_conf[lang] = conf
                    detected_languages_count[lang] = 1
        except ValueError as e:
            logging.info(e)

    # calculate the average confidence for each detected language
    detected_languages_avg_conf = {}
    for lang, total_conf in detected_languages_total_conf.items():
        detected_languages_avg_conf[lang] = (
            total_conf / detected_languages_count[lang]
        )

    return detected_languages_avg_conf


def detect_road_signs(image: Image.Image) -> list[npt.NDArray[np.uint8]]:
    """
    Get list of road signs image present on the image.

    Detects road signs in an input image and crops the image around each
    detected sign.

    @param image An input image to detect road signs from.
    @return A list of cropped image containing a detected road sign.
    """
    logging.info("detect_road_signs")

    # load YOLO model and set confidence threshold
    model = YOLO("weights/traffic_sign.pt")
    model.conf = 0.25

    # detect road signs in the image
    results = model(image)

    # crop each sign into its own image
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
    Process a road sign image for text detection and recognition.

    Processes the input image using a series of image processing techniques to
    isolate the text and remove background noise. Resulting image is always
    black text on white black background.

    @param image A numpy array representing the image to be processed.
    @return A numpty array reprensenting the image with isolated text.
    """
    # TODO: this still needs to be fixed for mypy
    logging.info("preprocess_images")

    # stretched_image
    stretched_image = first_process(image)
    cv2.imwrite("img/1.png", stretched_image)

    # get edges
    edges = get_edges(stretched_image)

    # get large connected component image
    component_image = get_component_images(edges)

    # get contour for shape approximation
    contour_image = get_contour(component_image)

    # compute polygon for shape
    try:
        quad = compute_polygon(contour_image)

        # correct perspective
        warped_image, warped_background = correct_perspective(
            stretched_image, component_image, quad
        )

        # final processing to clean up the image
        final = final_process(warped_image, warped_background)

        return final

    except ValueError as e:
        raise e


def first_process(image: npt.NDArray[np.uint8]) -> npt.NDArray[np.float32]:
    """
    Convert an image to grayscale and stretch the pixel intensity from 0 to 1.

    @param image The numpy image.
    @return A numpy image for the stretched grayscaled image.
    """
    logging.info("first_process")

    # convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # convert to float32
    gray = gray.astype(np.float32) / 255.0

    # stretch image
    stretched_image = cv2.normalize(
        gray, None, 0.0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F
    )

    # assert isinstance(stretched_image, np.ndarray) and stretched_image.dtype == np.float32, "filled must be of type ndarray[Any, dtype[floating[_32Bit]]]"

    return stretched_image


def get_edges(image: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
    """
    Apply a blur to an image and compute its edges.

    @param image A numpy image.
    @return A numpy image representing the binary edges of the image.
    """
    logging.info("get_edges")

    # apply blur
    blurred = cv2.GaussianBlur(image, (5, 5), 1.4)

    # compute gradient
    gx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
    gradient = cv2.magnitude(gx, gy)

    # get inverted binary
    _, binary_image = cv2.threshold(gradient, 0.1, 1.0, cv2.THRESH_BINARY)
    inverted_image = np.zeros_like(binary_image, dtype=np.float32)
    inverted_image = 1.0 - binary_image

    return inverted_image


def get_component_images(
    image: npt.NDArray[np.float32],
) -> npt.NDArray[np.uint8]:
    """
    Get the large connected component image.

    Get the connected components of an image and return the large connected
    components as a binary image.

    @param image A numpy image.
    @return A numpy image representing the large connected components as a
    binary image.
    """
    # get connected component
    logging.debug("get_component_images")

    # convert to uint8 as it is the required format for connected components
    inverted_image = (image * 255).astype(np.uint8)

    # get the connected components
    _, labels, stats, _ = cv2.connectedComponentsWithStats(inverted_image)

    # ensure stats is a list of tuples of integers
    # assert isinstance(stats, np.ndarray)
    # assert stats.ndim == 2
    # assert stats.shape[1] >= 5
    stats = stats.tolist()
    stats = [(i,) + tuple(x) for i, x in enumerate(stats)]

    # sort connected component
    stats = sorted(
        stats[1:], key=lambda x: x[cv2.CC_STAT_AREA + 1], reverse=True
    )

    # find largest connected component
    largest_area = stats[0][cv2.CC_STAT_AREA + 1]

    # create new connected component image that contain all connected component
    # bigger than 50% of the biggest
    component_image = np.zeros_like(inverted_image, dtype=np.uint8)
    for stat in stats:
        label = stat[0]
        area = stat[cv2.CC_STAT_AREA + 1]
        if area >= largest_area * 0.5:
            component_image[labels == label] = 255

    # find small holes
    kernel = np.ones((5, 5), np.uint8)
    filled = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    filled = fill_holes(filled)

    # assert for type safety
    # assert isinstance(filled, np.ndarray) and filled.dtype == np.uint8, "filled must be of type ndarray[Any, dtype[unsignedinteger[_8Bit]]]"

    return component_image


def get_contour(image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
    """
    Find the contour of the largest connected component in an image.

    @param image A numpy image.
    @return A numpy representing the contour of the largest connected component
    in the image.
    """
    logging.info("get_contour")

    # find countour of filled shape to correct perspective
    logging.debug("Finding contour of filled shape to correct pespective")
    contours, _ = cv2.findContours(
        image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    largest_contour = max(contours, key=cv2.contourArea)

    # assert for type safety
    # assert isinstance(largest_contour, np.ndarray) and largest_contour.dtype == np.uint8, "filled must be of type ndarray[Any, dtype[unsignedinteger[_8Bit]]]"

    return largest_contour


def compute_polygon(contour: npt.NDArray[np.uint8]) -> npt.NDArray[Any]:
    """
    Approximate the contour of a shape to a quad.

    Approximate the contour of the large connected components in an image with
    a quad.

    @param contour A numpy image representing a contour.
    @raise ValueError If the function fails to approximate the contour with a
    quad.
    @return A numpy array representing a quad approximating the input contour.
    """
    logging.info("compute_polygon")

    # initializes variable used for the approximation
    approx_quad = None
    max_iterations = 10
    iteration = 0

    # try to create a quand until we cant
    while (
        approx_quad is None or len(approx_quad) != 4
    ) and iteration < max_iterations:
        epsilon = (iteration + 1) * 0.01 * cv2.arcLength(contour, True)
        approx_quad = cv2.approxPolyDP(contour, epsilon, True)
        iteration += 1

    # if we have not been able to create a quad then we give up
    if approx_quad is None or len(approx_quad) != 4:
        raise ValueError("Failed to approximate polygon with 4 vertices.")

    # assert for type safety
    # assert isinstance(approx_quad, np.ndarray)
    # assert isinstance(filled, np.ndarray) and filled.dtype == np.uint8, "filled must be of type ndarray[Any, dtype[unsignedinteger[_8Bit]]]"

    return approx_quad


def correct_perspective(
    image: npt.NDArray[np.float32],
    component_image: npt.NDArray[np.uint8],
    quad: npt.NDArray[Any],
) -> tuple[npt.NDArray[np.uint8], npt.NDArray[np.uint8]]:
    """
    Correct perspective of the image based on its corners.

    @param image An imput image to correct the perspective of.
    @param component_image A binary image where the connected components should
    be 255.
    @param quad A set of four points representing the corners of a quad.
    @return A tuple with two elements - the corrected input image and the
    correct component image.
    """
    logging.info("correct_perspective")

    # organize data for correction
    src_pts = quad.reshape(4, 2).astype(np.float32)

    # order points
    src_pts_ordered = np.zeros_like(src_pts, dtype=np.float32)
    s = src_pts.sum(axis=1)
    src_pts_ordered[0] = src_pts[np.argmin(s)]
    src_pts_ordered[2] = src_pts[np.argmax(s)]
    d = np.diff(src_pts, axis=1)
    src_pts_ordered[1] = src_pts[np.argmin(d)]
    src_pts_ordered[3] = src_pts[np.argmax(d)]

    # compute dimensions of output image
    side_lengths = [
        np.linalg.norm(src_pts_ordered[i] - src_pts_ordered[i - 1])
        for i in range(4)
    ]
    output_height = int(round((side_lengths[0] + side_lengths[2]) / 2))
    output_width = int(round((side_lengths[1] + side_lengths[3]) / 2))

    # compute destination points for perspective transform
    dst_pts = np.array(
        [
            [0, 0],
            [output_width - 1, 0],
            [output_width - 1, output_height - 1],
            [0, output_height],
        ],
        dtype=np.float32,
    )

    # compute perspective matrix
    perspective_matrix = cv2.getPerspectiveTransform(src_pts_ordered, dst_pts)

    # apply perspective transform to the input image and the component image
    warped_image = cv2.warpPerspective(
        image, perspective_matrix, (output_width, output_height)
    )
    warped_background = cv2.warpPerspective(
        component_image, perspective_matrix, (output_width, output_height)
    )

    return warped_image, warped_background


def final_process(
    image: npt.NDArray[np.uint8], background: npt.NDArray[np.uint8]
) -> npt.NDArray[np.uint8]:
    """
    Apply a final processing to the image to obtain a clear text.

    @param image A numpy image.
    @param background A numpy binary image representing the background.
    @return A numpy image with black text on a white background.
    """
    logging.info("final_process")

    # doing a final stretching on the final image
    warped_stretched_image = cv2.normalize(
        image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U
    )

    # adding blur to text for reducing edge roughness
    text = cv2.GaussianBlur(warped_stretched_image, (3, 3), 1)

    # setting the text as black and the background as black
    text = extract_text(text, background)

    # assert for type safety
    # assert isinstance(text, np.ndarray) and text.dtype == np.uint8, "filled must be of type ndarray[Any, dtype[unsignedinteger[_8Bit]]]"

    return text


def detect_text(image: npt.NDArray[np.uint8]) -> dict[str, float]:
    """
    Detect the text in the given image.

    Detects the text in the given image and returns the text and corresponding
    confidence values.

    @param image A numpy array representing the image in the format of a 2D
    array of pixels.
    """
    logging.info("detect_text")

    # use pytesseract to get detected text
    data = pytesseract.image_to_data(
        image, output_type=pytesseract.Output.DICT
    )

    # create a dictionary from the resulting list
    text_and_confidences = {}
    for text, conf in zip(data["text"], data["conf"]):
        if int(conf) > 0 and text.strip():
            text_and_confidences[text] = float(conf)

    return text_and_confidences


def detect_languages(
    text_and_confidences: dict[str, float]
) -> dict[str, float]:
    """
    Detect the language present in the list of texts.

    Detects the language present in the list of texts and returns the language
    confidences as a dictionary.

    @param text_and_confidences A list of tuples containing the text ot detect
    the languages from and its confidence.
    @raise Exception An error occured during language detection.
    @return A dictionary where the jeys are the detected languages and the
    values are the confidence scores.
    """
    logging.info("detect_languages")

    # iterate trhough the images to get the languages
    language_confidences: dict[str, float] = defaultdict(int)
    min_text_length = 3
    for text, conf in text_and_confidences.items():
        # if the text is too small then we just skip it
        if len(text) < min_text_length:
            logging.debug(
                f"Skipping '{text}' as its length \
                    is below the minimum threshold"
            )
            continue
        try:
            # get language
            lang_detection = detect_langs(text)
            for lang in lang_detection:
                language_confidences[lang.lang] += lang.prob * conf * len(text)
        except Exception as e:
            logging.info(f"Skipping '{text}' as it caused lang_detect to fail")

    # compute total weight, if we didnt get anything return an empty directory
    total_weight = sum(language_confidences.values())
    if total_weight == 0:
        return {}

    # normalize the languages detected
    for lang in language_confidences:
        language_confidences[lang] /= total_weight

    return language_confidences


def extract_text(
    image: npt.NDArray[np.float32], mask: npt.NDArray[np.uint8]
) -> npt.NDArray[np.uint8]:
    """
    Extract text from an image using a given mask.

    @param image A numpy image representing the input image.
    @param mask A numpy image representing the binary mask.
    @return A numpy image representing the binary image with extracted text.
    """
    # compute the mean value of the image inside the mask
    mean = 0
    total = 0
    for j in range(image.shape[0]):
        for i in range(image.shape[1]):
            if mask[j, i] != 255:
                continue
            mean = mean + image[j, i]
            total = total + 1

    mean = int(np.rint(mean / total))

    # create a binary image by thresholding the image based on the mean value
    binary = np.zeros_like(image, dtype=np.uint8)
    for j in range(image.shape[0]):
        for i in range(image.shape[1]):
            if mask[j, i] == 255:
                continue
            if abs(image[j, i] - mean) > 50:
                binary[j, i] = 255

    binary = 255 - binary

    # apply morphological closing to the binary image
    kernel = np.ones((3, 3), np.uint8)
    closed_image = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # assert for type safety
    # assert isinstance(closed_image, np.ndarray) and closed_image.dtype == np.uint8, "filled must be of type ndarray[Any, dtype[unsignedinteger[_8Bit]]]"

    return closed_image


def fill_holes(image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
    """
    Fill holes in a binary image.

    Fills in holes in a binary image by ieterating throught the rows and
    columns of the image and filling in any white space found between two
    non-white spaces.

    @param A numpy image containing the binary image.
    @return A numpy image containing the filled binary image.
    """
    logging.info("fill_holes")

    # creating returned image
    filled = np.zeros_like(image, dtype=np.uint8)

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

    # assert for type safety
    # assert isinstance(filled, np.ndarray) and filled.dtype == np.uint8, "filled must be of type ndarray[Any, dtype[unsignedinteger[_8Bit]]]"

    return filled
