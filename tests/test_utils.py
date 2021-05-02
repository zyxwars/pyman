import unittest
from unittest import result
import utils
import json


class TestUtils(unittest.TestCase):
    def test_json_string_to_python(self):
        self.assertEqual(utils.json_string_to_python(
            """{"test": "testing", "1": 2}"""), {"test": "testing", "1": 2})

        self.assertEqual(utils.json_string_to_python(
            'Invalid json test string'), 'Invalid json test string')

    def test_format_json_string(self):
        self.assertEqual(utils.format_json_string(
            """{"test": "testing", "1": 2}"""), '{\n    "test": "testing",\n    "1": 2\n}')

        self.assertEqual(utils.format_json_string(
            'Invalid json test string'), 'Invalid json test string')


if __name__ == '__main__':
    unittest.main()
