class InvalidLanguageError(Exception):
    """Invalid language error."""


ALPHABET = {
    'abbr': {
        'es': ['d', 'h', 'm', 's', '', 'y'],
        'en': ['d', 'h', 'm', 's', '', 'and']
    },
    'default': {
        'es': ['día', 'hora', 'minuto', 'segundo', 's', 'y'],
        'en': ['day', 'hour', 'minute', 'second', 's', 'and']
    }
}


def seconds_to_str(seconds, abbreviated=False, integer=None, language='en'):
    """Returns seconds extended as string.

    Args:
        seconds (int, float): number of seconds.
        abbreviated (bool): use the abbreviated form or not.
        integer (bool): affects the type of the seconds. If set to true, seconds will always be int. If
            set to False, seconds will always be float. If not set (integer=None), seconds will be
            int if it has no decimals, if not it will be float.
        language (str): language to use.
    """

    if not isinstance(seconds, (float, int)):
        raise TypeError(f'seconds must be float or int, not {type(seconds).__name__}')

    if integer is True:
        seconds = int(seconds)

    try:
        if abbreviated is True:
            day_str, hour_str, minute_str, second_str, final_s, s_last = ALPHABET['abbr'][language]
        else:
            day_str, hour_str, minute_str, second_str, final_s, s_last = ALPHABET['default'][
                language]
    except KeyError:
        raise InvalidLanguageError(f'{language!r} is not a valid language')

    before = ", "
    s_last = ' ' + s_last + ' '
    has_before = [False, False, False, False]
    has_not_zero = [0, 0, 0, 0]

    day, hour, minute, second = _split_seconds(seconds, integer=integer, days=True)

    if second:
        last = 4
    elif minute:
        last = 3
    elif hour:
        last = 2
    elif day:
        last = 1
    else:
        last = 4

    if day:
        has_before[1] = True
        has_before[2] = True
        has_before[3] = True

        has_not_zero[0] = 1
    if hour:
        has_before[2] = True
        has_before[3] = True

        has_not_zero[1] = 1
    if minute:
        has_before[3] = True

        has_not_zero[2] = 1
    if second:
        has_not_zero[3] = 1

    only_one = sum(has_not_zero) == 1
    ret = ""

    if day:
        ret += "{} {}".format(day, day_str)
        if day - 1:
            ret += final_s
    if hour:
        if last == 2 and not only_one:
            ret += s_last
        elif has_before[1]:
            ret += before
        ret += "{} {}".format(hour, hour_str)
        if hour - 1:
            ret += final_s
    if minute:
        if last == 3 and not only_one:
            ret += s_last
        elif has_before[2]:
            ret += before
        ret += "{} {}".format(minute, minute_str)
        if minute - 1:
            ret += final_s
    if second:
        if last == 4 and not only_one:
            ret += s_last
        elif has_before[3]:
            ret += before
        ret += "{} {}".format(second, second_str)
        if second - 1:
            ret += final_s

    if second == minute == hour == day == 0:
        return '0 ' + second + final_s

    return ret


def _split_seconds(total_seconds, days=False, integer=None):
    """Transforma segundos en horas,minutos y segundos."""

    # total_seconds = int(total_seconds)

    total_minutes = total_seconds // 60
    seconds = total_seconds % 60
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)

    seconds = round(seconds, 2)

    if integer is True:
        seconds = int(seconds)
    elif integer is None:
        if seconds == int(seconds):
            seconds = int(seconds)

    if not days:
        return hours, minutes, seconds
    else:
        days = hours // 24
        hours = hours % 24
        return days, hours, minutes, seconds
