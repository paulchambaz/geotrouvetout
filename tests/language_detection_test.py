import pytest
from geotrouvetout import detect_languages


def test_detect_languages():
    text_and_confidences = [("Hello world", 0.5)]
    languages = detect_languages(text_and_confidences)
    assert languages[0][0] == "en"
