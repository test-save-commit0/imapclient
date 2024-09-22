"""
A lexical analyzer class for IMAP responses.

Although Lexer does all the work, TokenSource is the class to use for
external callers.
"""
from typing import Iterator, List, Optional, Tuple, TYPE_CHECKING, Union
from .util import assert_imap_protocol
__all__ = ['TokenSource']
CTRL_CHARS = frozenset(c for c in range(32))
ALL_CHARS = frozenset(c for c in range(256))
SPECIALS = frozenset(c for c in b' ()%"[')
NON_SPECIALS = ALL_CHARS - SPECIALS - CTRL_CHARS
WHITESPACE = frozenset(c for c in b' \t\r\n')
BACKSLASH = ord('\\')
OPEN_SQUARE = ord('[')
CLOSE_SQUARE = ord(']')
DOUBLE_QUOTE = ord('"')


class TokenSource:
    """
    A simple iterator for the Lexer class that also provides access to
    the current IMAP literal.
    """

    def __init__(self, text: List[bytes]):
        self.lex = Lexer(text)
        self.src = iter(self.lex)

    def __iter__(self) ->Iterator[bytes]:
        return self.src


class Lexer:
    """
    A lexical analyzer class for IMAP
    """

    def __init__(self, text: List[bytes]):
        self.sources = (LiteralHandlingIter(chunk) for chunk in text)
        self.current_source: Optional[LiteralHandlingIter] = None

    def __iter__(self) ->Iterator[bytes]:
        for source in self.sources:
            self.current_source = source
            for tok in self.read_token_stream(iter(source)):
                yield bytes(tok)


class LiteralHandlingIter:

    def __init__(self, resp_record: Union[Tuple[bytes, bytes], bytes]):
        self.literal: Optional[bytes]
        if isinstance(resp_record, tuple):
            self.src_text = resp_record[0]
            assert_imap_protocol(self.src_text.endswith(b'}'), self.src_text)
            self.literal = resp_record[1]
        else:
            self.src_text = resp_record
            self.literal = None

    def __iter__(self) ->'PushableIterator':
        return PushableIterator(self.src_text)


class PushableIterator:
    NO_MORE = object()

    def __init__(self, it: bytes):
        self.it = iter(it)
        self.pushed: List[int] = []

    def __iter__(self) ->'PushableIterator':
        return self

    def __next__(self) ->int:
        if self.pushed:
            return self.pushed.pop()
        return next(self.it)
    next = __next__
