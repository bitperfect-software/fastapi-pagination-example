import json

from pydantic import BeforeValidator


def convert_items_to_json(x: list[str]) -> list[dict]:
    items = []
    try:
        for item in x:
            items.append(json.loads(item))
    except Exception:
        return items
    return items

StringDictValidator = BeforeValidator(lambda x: convert_items_to_json(x) if x is not None else [])