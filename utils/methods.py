"""Contains a little method that we use multiple times."""
import re
from datetime import timedelta


class ParseTimeException(Exception):
    pass


def parse_time(time_str):
    """Convert a str into datetime.timedelta.

    The string needs to mathe the regex :
        r'((?P<days>\\d+?)d ?)?((?P<hours>\\d+?)h ?)?((?P<minutes>\\d+?)m ?)?'
    """
    regex = re.compile(r'((?P<days>\d+?)d ?)?((?P<hours>\d+?)h ?)?((?P<minutes>\d+?)m ?)?')
    parts = regex.match(time_str)
    parts = parts.groupdict()
    valid = False
    for value in parts.values():
        if value:
            valid = True
    if not valid:
        raise ParseTimeException()
    time_params = {}
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)
