from dataclasses import dataclass

from .exceptions import InvalidLanguageError

ALPHABET = {
    "abbr": {
        "es": ["d", "h", "m", "s", "", "y"],
        "en": ["d", "h", "m", "s", "", "and"],
    },
    "default": {
        "es": ["día", "hora", "minuto", "segundo", "s", "y"],
        "en": ["day", "hour", "minute", "second", "s", "and"],
    },
}


@dataclass
class Language:
    day: str
    hour: str
    minute: str
    second: str
    s: str
    join: str


LANGUAGES = {
    "abbr": {k: Language(*v) for k, v in ALPHABET["abbr"].items()},
    "default": {k: Language(*v) for k, v in ALPHABET["default"].items()},
}


def seconds_to_str(seconds, abbreviated=False, integer=None, language="en"):
    """Returns seconds extended as string.

    Args:
        seconds (int, float): number of seconds.
        abbreviated (bool): use the abbreviated form or not.
        integer (bool): affects the type of the seconds. If set to true, seconds will always be
            int. If set to False, seconds will always be float. If not set (integer=None),
            seconds will be int if it has no decimals, if not it will be float.
        language (str): language to use.
    """

    if not isinstance(seconds, (float, int)):
        raise TypeError(f"seconds must be float or int, not {type(seconds).__name__}")

    try:
        if abbreviated is True:
            language = LANGUAGES["abbr"][language]
        else:
            language = LANGUAGES["default"][language]
    except KeyError:
        raise InvalidLanguageError(f"{language!r} is not a valid language")

    try:
        int(seconds)
    except OverflowError:
        return "infinite %s%s" % (language.day, language.s)

    day, hour, minute, second = split_seconds(seconds, integer=integer, days=True)

    day_part = gen_part(day, language.day, language.s, abbreviated)
    hour_part = gen_part(hour, language.hour, language.s, abbreviated)
    minute_part = gen_part(minute, language.minute, language.s, abbreviated)
    second_part = gen_part(second, language.second, language.s, abbreviated)

    # breakpoint()
    output = join_parts(language.join, day_part, hour_part, minute_part, second_part)

    if not output:
        return gen_part(
            0, language.second, language.s, abbreviated, force_output=True
        )
    return output


def gen_part(int_part, str_part, possible_s, is_abbr, force_output=False):
    if not int_part and not force_output:
        return None

    output = str(int_part)
    if not is_abbr:
        output += " "

    output += str_part

    if int_part - 1 and not is_abbr:
        output += possible_s
    return output


def join_parts(join_str, *string_parts):
    string_parts = [x for x in string_parts if x]

    if not string_parts:
        return None

    if len(string_parts) == 1:
        return string_parts[0]

    output = ", ".join(string_parts[:-1])
    return output + " " + join_str + " " + string_parts[-1]


def split_seconds(total_seconds, days=False, integer=None):
    """[summary]

    Args:
        total_seconds (int or float): total number of seconds.
        days (bool, optional): If true, it will return a 4-length tuple,
            including the days. Defaults to False.
        integer (bool or None, optional): If True, the seconds returned
            will be an integer. If False, no conversion will be made. If
            None and the remaining seconds are 0, it will return the
            seconds (0) as an int, regardless that it was int or float.
            Defaults to None.

    Returns:
        tuple: 3-length tuple: (hours, seconds, minutes). If days is True,
        it will be a 4-length tuple: (days, hours, seconds, minutes).
    """

    # total_seconds = int(total_seconds)

    total_minutes = total_seconds // 60
    seconds = total_seconds % 60
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)

    seconds = round(seconds, 2)

    if integer is True:
        seconds = round(seconds, 0)
    elif integer is None:
        if seconds == int(seconds):
            seconds = int(seconds)

    if not days:
        return hours, minutes, seconds

    days = hours // 24
    hours = hours % 24
    return days, hours, minutes, seconds
