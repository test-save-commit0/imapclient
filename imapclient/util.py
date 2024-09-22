import logging
from typing import Iterator, Optional, Tuple, Union
from . import exceptions
logger = logging.getLogger(__name__)
_TupleAtomPart = Union[None, int, bytes]
_TupleAtom = Tuple[Union[_TupleAtomPart, '_TupleAtom'], ...]
