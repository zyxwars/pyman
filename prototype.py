import json
import requests

s = """{"name": "First Las",
     "email": "first.last@mail.com",
     "myArray": [100, 200, 300]}"""

test = json.loads(s)
test = json.dumps(test, indent=4)
print(type(test))
