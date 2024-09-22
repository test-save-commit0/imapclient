"""
Parsing for IMAP command responses with focus on FETCH responses as
returned by imaplib.

Initially inspired by http://effbot.org/zone/simple-iterator-parser.htm
"""
import datetime
import re
import sys
from collections import defaultdict
from typing import cast, Dict, Iterator, List, Optional, Tuple, TYPE_CHECKING, Union
from .datetime_util import parse_to_datetime
from .exceptions import ProtocolError
from .response_lexer import TokenSource
from .response_types import Address, BodyData, Envelope, SearchIds
from .typing_imapclient import _Atom
__all__ = ['parse_response', 'parse_message_list']


def parse_response(data: List[bytes]) ->Tuple[_Atom, ...]:
    """Pull apart IMAP command responses.

    Returns nested tuples of appropriately typed objects.
    """
    pass


_msg_id_pattern = re.compile('(\\d+(?: +\\d+)*)')


def parse_message_list(data: List[Union[bytes, str]]) ->SearchIds:
    """Parse a list of message ids and return them as a list.

    parse_response is also capable of doing this but this is
    faster. This also has special handling of the optional MODSEQ part
    of a SEARCH response.

    The returned list is a SearchIds instance which has a *modseq*
    attribute which contains the MODSEQ response (if returned by the
    server).
    """
    pass


_ParseFetchResponseInnerDict = Dict[bytes, Optional[Union[datetime.datetime,
    int, BodyData, Envelope, _Atom]]]


def parse_fetch_response(text: List[bytes], normalise_times: bool=True,
    uid_is_key: bool=True) ->'defaultdict[int, _ParseFetchResponseInnerDict]':
    """Pull apart IMAP FETCH responses as returned by imaplib.

    Returns a dictionary, keyed by message ID. Each value a dictionary
    keyed by FETCH field type (eg."RFC822").
    """
    pass
