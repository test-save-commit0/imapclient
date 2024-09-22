import argparse
import configparser
import json
import os
import ssl
import urllib.parse
import urllib.request
from typing import Any, Callable, Dict, Optional, Tuple, TYPE_CHECKING, TypeVar
import imapclient


def parse_config_file(filename: str) ->argparse.Namespace:
    """Parse INI files containing IMAP connection details.

    Used by livetest.py and interact.py
    """
    pass


T = TypeVar('T')
OAUTH2_REFRESH_URLS = {'imap.gmail.com':
    'https://accounts.google.com/o/oauth2/token', 'imap.mail.yahoo.com':
    'https://api.login.yahoo.com/oauth2/get_token'}
_oauth2_cache: Dict[Tuple[str, str, str, str], str] = {}
