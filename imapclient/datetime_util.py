import re
from datetime import datetime
from email.utils import parsedate_tz
from .fixed_offset import FixedOffset
_SHORT_MONTHS = ' Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ')


def parse_to_datetime(timestamp: bytes, normalise: bool=True) ->datetime:
    """Convert an IMAP datetime string to a datetime.

    If normalise is True (the default), then the returned datetime
    will be timezone-naive but adjusted to the local time.

    If normalise is False, then the returned datetime will be
    unadjusted but will contain timezone information as per the input.
    """
    if isinstance(timestamp, bytes):
        timestamp = timestamp.decode('ascii')
    
    tt = parsedate_tz(timestamp)
    if tt is None:
        raise ValueError("Could not parse datetime string: %r" % timestamp)

    tz = tt[-1]
    dt = datetime(*tt[:6], tzinfo=FixedOffset(tz) if tz else None)

    if normalise:
        return dt.astimezone().replace(tzinfo=None)
    return dt


def datetime_to_INTERNALDATE(dt: datetime) ->str:
    """Convert a datetime instance to a IMAP INTERNALDATE string.

    If timezone information is missing the current system
    timezone is used.
    """
    if dt.tzinfo is None:
        dt = dt.astimezone()
    
    return dt.strftime("%d-%b-%Y %H:%M:%S %z")


_rfc822_dotted_time = re.compile(
    '\\w+, ?\\d{1,2} \\w+ \\d\\d(\\d\\d)? \\d\\d?\\.\\d\\d?\\.\\d\\d?.*')


def format_criteria_date(dt: datetime) ->bytes:
    """Format a date or datetime instance for use in IMAP search criteria."""
    if isinstance(dt, datetime):
        dt = dt.date()
    return dt.strftime("%d-%b-%Y").encode('ascii')
