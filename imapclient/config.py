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
    config = configparser.ConfigParser()
    config.read(filename)

    if 'DEFAULT' not in config:
        raise ValueError(f"Config file {filename} must have a DEFAULT section")

    ns = argparse.Namespace()
    for key, value in config['DEFAULT'].items():
        setattr(ns, key, value)

    # Convert certain values to appropriate types
    if hasattr(ns, 'port'):
        ns.port = int(ns.port)
    if hasattr(ns, 'ssl'):
        ns.ssl = config['DEFAULT'].getboolean('ssl')
    if hasattr(ns, 'timeout'):
        ns.timeout = float(ns.timeout)

    return ns


T = TypeVar('T')
OAUTH2_REFRESH_URLS = {'imap.gmail.com':
    'https://accounts.google.com/o/oauth2/token', 'imap.mail.yahoo.com':
    'https://api.login.yahoo.com/oauth2/get_token'}
_oauth2_cache: Dict[Tuple[str, str, str, str], str] = {}
