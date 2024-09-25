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
            yield _convert_token(token, lexer.current_literal)
        else:
            raise ProtocolError(f'Unexpected token: {token}')

def _convert_token(token: bytes, literal: Optional[bytes]) ->_Atom:
    if literal is not None:
        return literal
    try:
        return int(token)
    except ValueError:
        return token


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
    search_ids = SearchIds(ids)
    
    if modseq:
        search_ids.modseq = modseq
    
    return search_ids


_ParseFetchResponseInnerDict = Dict[bytes, Optional[Union[datetime.datetime,
    int, BodyData, Envelope, _Atom]]]


def parse_fetch_response(text: List[bytes], normalise_times: bool=True,
    uid_is_key: bool=True) ->'defaultdict[int, _ParseFetchResponseInnerDict]':
    """Pull apart IMAP FETCH responses as returned by imaplib.

    Returns a dictionary, keyed by message ID. Each value a dictionary
    keyed by FETCH field type (eg."RFC822").
    """
    response = defaultdict(dict)
    for response_item in parse_response(text):
        msg_id, fetch_data = response_item
        msg_id = int(msg_id)
        
        for field, value in _parse_fetch_pairs(fetch_data):
            field = field.upper()
            
            if field == b'UID' and uid_is_key:
                msg_id = value
            elif field == b'INTERNALDATE' and normalise_times:
                value = parse_to_datetime(value)
            elif field in (b'BODY', b'BODY.PEEK'):
                value = BodyData(value)
            elif field == b'ENVELOPE':
                value = Envelope(*value)
            
            response[msg_id][field] = value
    
    return response

def _parse_fetch_pairs(fetch_data: Tuple[_Atom, ...]) ->Iterator[Tuple[bytes, _Atom]]:
    for i in range(0, len(fetch_data), 2):
        field = fetch_data[i]
        if not isinstance(field, bytes):
            raise ProtocolError(f'Field name must be bytes: {field}')
        yield field, fetch_data[i + 1]
