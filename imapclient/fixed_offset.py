import datetime
import time
from typing import Optional
ZERO = datetime.timedelta(0)


class FixedOffset(datetime.tzinfo):
    """
    This class describes fixed timezone offsets in hours and minutes
    east from UTC
    """

    def __init__(self, minutes: float) ->None:
        self.__offset = datetime.timedelta(minutes=minutes)
        sign = '+'
        if minutes < 0:
            sign = '-'
        hours, remaining_mins = divmod(abs(minutes), 60)
        self.__name = '%s%02d%02d' % (sign, hours, remaining_mins)

    @classmethod
    def for_system(cls) ->'FixedOffset':
        """Return a FixedOffset instance for the current working timezone and
        DST conditions.
        """
        if time.daylight:
            offset = time.altzone
        else:
            offset = time.timezone
        return cls(-offset // 60)
