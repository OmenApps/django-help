"""Regex utilities for Django."""

import logging
from typing import Union

from django.http import HttpRequest


logger = logging.getLogger(__name__)


def get_path_regex(request_or_path: Union[HttpRequest, str]) -> str:
    """Returns a regex pattern that matches the current path."""

    # If the input is an HttpRequest, get the current path
    if isinstance(request_or_path, HttpRequest):
        current_path = request_or_path.path
    else:
        current_path = request_or_path

    # Convert the path to a regex pattern, replacing '*' with '.*'
    # and anchoring it to match the entire string
    return "^" + current_path.replace("*", ".*") + "$"
