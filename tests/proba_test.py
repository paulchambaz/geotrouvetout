import unittest
from geotrouvetout import detect_languages


class TestDetectLanguages(unittest.TestCase):

    def test_detect_languages(self):
        text_and_confidences = [("Hello, how are you?", 0.8), ("Bonjour, comment allez-vous?", 0.6), ("こんにちは、お元気ですか？", 0.7)]
        expected_output = [("en", 0.51953125), ("ja", 0.328125), ("fr", 0.15234375)]

        result = detect_languages(text_and_confidences)
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()
