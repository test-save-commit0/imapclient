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
    lexer = TokenSource(data)
    return tuple(_parse_tokens(lexer))

def _parse_tokens(lexer: TokenSource) ->Iterator[_Atom]:
    for token in lexer:
        if token == b'(':
            yield tuple(_parse_tokens(lexer))
        elif token == b')':
            return
        elif isinstance(token, bytes):
            yield token.decode('ascii')
        else:
            yield token


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
    data = [item.decode('ascii') if isinstance(item, bytes) else item for item in data]
    data = ' '.join(data)
    
    modseq = None
    if 'MODSEQ' in data:
        modseq_index = data.index('MODSEQ')
        modseq = int(data[modseq_index + 1])
        data = data[:modseq_index]
    
    ids = [int(num) for num in _msg_id_pattern.findall(data)]
    return SearchIds(ids, modseq)


_ParseFetchResponseInnerDict = Dict[bytes, Optional[Union[datetime.datetime,
    int, BodyData, Envelope, _Atom]]]


def parse_fetch_response(text: List[bytes], normalise_times: bool=True,
    uid_is_key: bool=True) ->'defaultdict[int, _ParseFetchResponseInnerDict]':
    """Pull apart IMAP FETCH responses as returned by imaplib.

    Returns a dictionary, keyed by message ID. Each value a dictionary
    keyed by FETCH field type (eg."RFC822").
    """
    response = defaultdict(dict)
    lexer = TokenSource(text)

    while True:
        try:
            msg_id = int(next(lexer))
        except StopIteration:
            break

        if next(lexer) != b'(':
            raise ProtocolError('Expected "(" in FETCH response')

        for key, value in _parse_fetch_pairs(lexer, normalise_times):
            if uid_is_key and key == b'UID':
                msg_id = value
            else:
                response[msg_id][key] = value

        if next(lexer) != b')':
            raise ProtocolError('Expected ")" in FETCH response')

    return response

def _parse_fetch_pairs(lexer: TokenSource, normalise_times: bool) ->Iterator[Tuple[bytes, Union[datetime.datetime, int, BodyData, Envelope, _Atom]]]:
    while True:
        try:
            key = next(lexer)
        except StopIteration:
            return

        if key == b')':
            lexer.push(key)
            return

        value = _parse_fetch_value(lexer, key, normalise_times)
        yield key, value

def _parse_fetch_value(lexer: TokenSource, key: bytes, normalise_times: bool) ->Union[datetime.datetime, int, BodyData, Envelope, _Atom]:
    if key in (b'INTERNALDATE', b'ENVELOPE'):
        value = next(lexer)
        if key == b'INTERNALDATE' and normalise_times:
            return parse_to_datetime(value.decode('ascii'))
        elif key == b'ENVELOPE':
            return Envelope(*parse_response(value))
    elif key == b'BODY' and next(lexer) == b'[':
        section = b''
        while True:
            token = next(lexer)
            if token == b']':
                break
            section += token
        next(lexer)  # Consume the space
        value = next(lexer)
        return BodyData(section, value)
    else:
        value = next(lexer)
        if isinstance(value, int):
            return value
        return value.decode('ascii')
