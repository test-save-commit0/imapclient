from typing import Any, Dict
from unittest.mock import Mock
from .imapclient import IMAPClient


class TestableIMAPClient(IMAPClient):
    """Wrapper of :py:class:`imapclient.IMAPClient` that mocks all
    interaction with real IMAP server.

    This class should only be used in tests, where you can safely
    interact with imapclient without running commands on a real
    IMAP account.
    """

    def __init__(self) ->None:
        super().__init__('somehost')


class MockIMAP4(Mock):

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.use_uid = True
        self.sent = b''
        self.tagged_commands: Dict[Any, Any] = {}
        self._starttls_done = False
