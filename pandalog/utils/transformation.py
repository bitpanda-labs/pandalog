from __future__ import annotations
import urllib.parse


def to_grn(entity: str, name: str) -> str:
    """returns a Graylog GRN formatted entity name"""

    return f"grn::::{entity}:{name}"


def to_url(uri: str) -> str:
    """returns a URL-friendly URI"""

    return urllib.parse.quote_plus(uri)
