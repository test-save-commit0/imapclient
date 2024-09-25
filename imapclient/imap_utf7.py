import base64
import binascii
from typing import List, Union


def encode(s: Union[str, bytes]) ->bytes:
    """Encode a folder name using IMAP modified UTF-7 encoding.

    Input is unicode; output is bytes (Python 3) or str (Python 2). If
    non-unicode input is provided, the input is returned unchanged.
    """
    if isinstance(s, bytes):
        return s
    if not isinstance(s, str):
        raise ValueError("Input must be str or bytes")
    
    result = bytearray()
    utf7_buffer = bytearray()
    
    for char in s:
        if ord(char) in range(0x20, 0x7f) and char != '&':
            if utf7_buffer:
                result.extend(b'&' + base64.b64encode(utf7_buffer).rstrip(b'=').replace(b'/', b',') + b'-')
                utf7_buffer = bytearray()
            result.extend(char.encode('ascii'))
        else:
            utf7_buffer.extend(char.encode('utf-16be'))
    
    if utf7_buffer:
        result.extend(b'&' + base64.b64encode(utf7_buffer).rstrip(b'=').replace(b'/', b',') + b'-')
    
    return bytes(result)


AMPERSAND_ORD = ord('&')
DASH_ORD = ord('-')


def decode(s: Union[bytes, str]) ->str:
    """Decode a folder name from IMAP modified UTF-7 encoding to unicode.

    Input is bytes (Python 3) or str (Python 2); output is always
    unicode. If non-bytes/str input is provided, the input is returned
    unchanged.
    """
    if isinstance(s, str):
        s = s.encode('ascii')
    if not isinstance(s, bytes):
        raise ValueError("Input must be str or bytes")
    
    result = []
    utf7_buffer = bytearray()
    is_utf7 = False
    
    for byte in s:
        if is_utf7:
            if byte == DASH_ORD:
                if utf7_buffer:
                    padded = utf7_buffer + b'=' * ((4 - len(utf7_buffer) % 4) % 4)
                    decoded = base64.b64decode(padded.replace(b',', b'/'))
                    result.append(decoded.decode('utf-16be'))
                    utf7_buffer = bytearray()
                is_utf7 = False
            elif byte == AMPERSAND_ORD:
                utf7_buffer.append(byte)
                result.append('&')
            else:
                utf7_buffer.append(byte)
        elif byte == AMPERSAND_ORD:
            is_utf7 = True
        else:
            result.append(chr(byte))
    
    return ''.join(result)
