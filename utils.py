import re
from json.decoder import JSONDecodeError
import json
from requests.structures import CaseInsensitiveDict


def json_to_python(json_string: str):
    """If conversion fails, return empty dict."""
    try:
        python_type = json.loads(json_string)
    except JSONDecodeError:
        python_type = {}

    return python_type


def python_to_json(python_type, indent=4):
    """json.dumps convenience wrapper"""
    return json.dumps(python_type, indent=indent)


def format_json(json_string: str) -> str:
    """If conversion fails, return original string."""
    try:
        python_type = json.loads(json_string)
        json_string = json.dumps(python_type, indent=4)
    except JSONDecodeError:
        pass

    return json_string


def is_json(json_string: str) -> bool:
    try:
        json.loads(json_string)
    except JSONDecodeError:
        return False
    return True


def add_item_to_json(current_json: str, key, value):
    caseless_dict = CaseInsensitiveDict(json_to_python(current_json))
    caseless_dict[key] = value
    return python_to_json(dict(caseless_dict))
