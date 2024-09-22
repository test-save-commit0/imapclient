import binascii
from typing import List, Union


def encode(s: Union[str, bytes]) ->bytes:
    """Encode a folder name using IMAP modified UTF-7 encoding.

    Input is unicode; output is bytes (Python 3) or str (Python 2). If
    non-unicode input is provided, the input is returned unchanged.
    """
    pass


AMPERSAND_ORD = ord('&')
DASH_ORD = ord('-')


def decode(s: Union[bytes, str]) ->str:
    """Decode a folder name from IMAP modified UTF-7 encoding to unicode.

    Input is bytes (Python 3) or str (Python 2); output is always
    unicode. If non-bytes/str input is provided, the input is returned
    unchanged.
    """
    pass
