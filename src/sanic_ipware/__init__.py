__version__ = "0.1.0"

import logging

from . import utils
from .ipware import get_client_ip

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ("get_client_ip", "utils")
