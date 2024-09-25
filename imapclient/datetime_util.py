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
    
    time_tuple = parsedate_tz(timestamp)
    if time_tuple is None:
        raise ValueError("Invalid timestamp format")
    
    tz_offset = time_tuple[-1]
    dt = datetime(*time_tuple[:6], tzinfo=FixedOffset(tz_offset) if tz_offset else None)
    
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
    
    return dt.strftime("%d-%b-%Y %H:%M:%S %z").strip()


_rfc822_dotted_time = re.compile(
    '\\w+, ?\\d{1,2} \\w+ \\d\\d(\\d\\d)? \\d\\d?\\.\\d\\d?\\.\\d\\d?.*')


def format_criteria_date(dt: datetime) ->bytes:
    """Format a date or datetime instance for use in IMAP search criteria."""
    if isinstance(dt, datetime):
        dt_str = dt.strftime("%d-%b-%Y")
    else:
        dt_str = dt.strftime("%d-%b-%Y")
    
    return dt_str.encode('ascii')
