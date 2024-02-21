from datetime import datetime


def custom_json_encoder(obj):
    """Перевести дату в формат для json."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class CustomException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
