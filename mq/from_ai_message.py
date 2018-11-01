import json


def from_ai_message(payload):
    return json.loads(payload)
