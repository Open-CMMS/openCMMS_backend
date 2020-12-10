import re
from datetime import timedelta


class ParseTimeException(Exception):
    pass


def parse_time(time_str):
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
