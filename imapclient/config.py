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
    ns.host = config['DEFAULT'].get('host', 'imap.gmail.com')
    ns.port = config['DEFAULT'].getint('port', 993)
    ns.ssl = config['DEFAULT'].getboolean('ssl', True)
    ns.username = config['DEFAULT'].get('username')
    ns.password = config['DEFAULT'].get('password')
    ns.oauth2 = config['DEFAULT'].getboolean('oauth2', False)
    ns.oauth2_client_id = config['DEFAULT'].get('oauth2_client_id')
    ns.oauth2_client_secret = config['DEFAULT'].get('oauth2_client_secret')
    ns.oauth2_refresh_token = config['DEFAULT'].get('oauth2_refresh_token')

    if ns.oauth2 and (not ns.oauth2_client_id or not ns.oauth2_client_secret or not ns.oauth2_refresh_token):
        raise ValueError("oauth2_client_id, oauth2_client_secret, and oauth2_refresh_token must be provided when oauth2 is True")

    return ns


T = TypeVar('T')
OAUTH2_REFRESH_URLS = {'imap.gmail.com':
    'https://accounts.google.com/o/oauth2/token', 'imap.mail.yahoo.com':
    'https://api.login.yahoo.com/oauth2/get_token'}
_oauth2_cache: Dict[Tuple[str, str, str, str], str] = {}
