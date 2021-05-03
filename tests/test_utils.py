import unittest
from unittest import result
import utils
import json


class TestUtils(unittest.TestCase):
    def test_json__to_python(self):
        self.assertEqual(utils.json_to_python(
            """{"test": "testing", "1": 2}"""), {"test": "testing", "1": 2})

        self.assertEqual(utils.json_to_python('Not json'), {})

    def test_format_json(self):
        self.assertEqual(utils.format_json(
            """{"test": "testing", "1": 2}"""), '{\n    "test": "testing",\n    "1": 2\n}')

        self.assertEqual(utils.format_json(
            'Invalid json test string'), 'Invalid json test string')

    def test_is_json(self):
        self.assertTrue(utils.is_json('{"test": "testing", "1": 2}'))

        self.assertFalse(utils.is_json('{"test": "testing", '))

        self.assertTrue(utils.is_json('[1, 2, 5]'))

        self.assertTrue(utils.is_json(
            '[{"test": "testing"}, {"test": "testing"}]'))

        self.assertTrue(utils.is_json('[{"test": "testing", "1": 2}]'))


if __name__ == '__main__':
    unittest.main()
