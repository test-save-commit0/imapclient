import imaplib
import socket
from typing import Optional


class IMAP4WithTimeout(imaplib.IMAP4):

    def __init__(self, address: str, port: int, timeout: Optional[float]
        ) ->None:
        self._timeout = timeout
        imaplib.IMAP4.__init__(self, address, port)
