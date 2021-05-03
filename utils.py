import re
from json.decoder import JSONDecodeError
import json


def json_string_to_python(json_string: str) -> str:
    """If conversion fails, return original."""
    python_type = json_string
    try:
        python_type = json.loads(python_type)
    except JSONDecodeError:
        pass

    return python_type


def format_json_string(json_string: str) -> str:
    """If conversion fails, return original."""
    try:
        python_type = json.loads(json_string)
        json_string = json.dumps(python_type, indent=4)
    except JSONDecodeError:
        pass

    return json_string


def is_json(json_string: str) -> bool:
    """Match json or json array."""
    # https://docs.python.org/2/library/re.html#search-vs-match
    return bool(re.match(r'^{.*}$|^\[.*\]$', json_string))
