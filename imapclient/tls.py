"""
This module contains IMAPClient's functionality related to Transport
Layer Security (TLS a.k.a. SSL).
"""
import imaplib
import io
import socket
import ssl
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from typing_extensions import Buffer


class IMAP4_TLS(imaplib.IMAP4):
    """IMAP4 client class for TLS/SSL connections.

    Adapted from imaplib.IMAP4_SSL.
    """

    def __init__(self, host: str, port: int, ssl_context: Optional[ssl.
        SSLContext], timeout: Optional[float]=None):
        self.ssl_context = ssl_context
        self._timeout = timeout
        imaplib.IMAP4.__init__(self, host, port)
        self.file: io.BufferedReader
