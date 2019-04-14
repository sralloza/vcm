import pytest

from vcd.time_operations import seconds_to_str, InvalidLanguageError


def test_invalid_language_error():
    with pytest.raises(InvalidLanguageError):
        raise InvalidLanguageError


def test_seconds_to_str_1():
    assert seconds_to_str(2.02) == '2.02 seconds'
    assert seconds_to_str(122.02) == '2 minutes and 2.02 seconds'
    assert seconds_to_str(7322.02) == '2 hours, 2 minutes and 2.02 seconds'

    assert seconds_to_str(2.02, integer=True) == '2 seconds'
    assert seconds_to_str(122.02, integer=True) == '2 minutes and 2 seconds'
    assert seconds_to_str(7322.02, integer=True) == '2 hours, 2 minutes and 2 seconds'

    assert seconds_to_str(3650) == '1 hour and 50 seconds'
    assert seconds_to_str(3650.4) == '1 hour and 50.4 seconds'
    assert seconds_to_str(86450) == '1 day and 50 seconds'
    assert seconds_to_str(86450.7) == '1 day and 50.7 seconds'

    assert seconds_to_str(356) == '5 minutes and 56 seconds'
    assert seconds_to_str(356.321) == '5 minutes and 56.32 seconds'
    assert seconds_to_str(635) == '10 minutes and 35 seconds'
    assert seconds_to_str(635.65) == '10 minutes and 35.65 seconds'
    assert seconds_to_str(6584) == '1 hour, 49 minutes and 44 seconds'
    assert seconds_to_str(6584.1) == '1 hour, 49 minutes and 44.1 seconds'
    assert seconds_to_str(6950) == '1 hour, 55 minutes and 50 seconds'
    assert seconds_to_str(6950.13) == '1 hour, 55 minutes and 50.13 seconds'

    assert seconds_to_str(98798) == '1 day, 3 hours, 26 minutes and 38 seconds'
    assert seconds_to_str(98798.95) == '1 day, 3 hours, 26 minutes and 38.95 seconds'
    assert seconds_to_str(654233) == '7 days, 13 hours, 43 minutes and 53 seconds'
    assert seconds_to_str(654233.2) == '7 days, 13 hours, 43 minutes and 53.2 seconds'
    assert seconds_to_str(654984) == '7 days, 13 hours, 56 minutes and 24 seconds'
    assert seconds_to_str(654984.1) == '7 days, 13 hours, 56 minutes and 24.1 seconds'
    assert seconds_to_str(1989469) == '23 days, 37 minutes and 49 seconds'
    assert seconds_to_str(1989469.5) == '23 days, 37 minutes and 49.5 seconds'


def test_seconds_to_str_2():
    with pytest.raises(InvalidLanguageError):
        seconds_to_str(1, language='invalid')


def test_seconds_to_str_3():
    assert seconds_to_str(2.02, language='es') == '2.02 segundos'
    assert seconds_to_str(122.02, language='es') == '2 minutos y 2.02 segundos'
    assert seconds_to_str(7322.02, language='es') == '2 horas, 2 minutos y 2.02 segundos'

    assert seconds_to_str(2.02, integer=True, language='es') == '2 segundos'
    assert seconds_to_str(122.02, integer=True, language='es') == '2 minutos y 2 segundos'
    assert seconds_to_str(7322.02, integer=True, language='es') == '2 horas, 2 minutos y 2 segundos'

    assert seconds_to_str(3650, language='es') == '1 hora y 50 segundos'
    assert seconds_to_str(3650.4, language='es') == '1 hora y 50.4 segundos'
    assert seconds_to_str(86450, language='es') == '1 día y 50 segundos'
    assert seconds_to_str(86450.7, language='es') == '1 día y 50.7 segundos'

    assert seconds_to_str(356, language='es') == '5 minutos y 56 segundos'
    assert seconds_to_str(356.321, language='es') == '5 minutos y 56.32 segundos'
    assert seconds_to_str(635, language='es') == '10 minutos y 35 segundos'
    assert seconds_to_str(635.65, language='es') == '10 minutos y 35.65 segundos'
    assert seconds_to_str(6584, language='es') == '1 hora, 49 minutos y 44 segundos'
    assert seconds_to_str(6584.1, language='es') == '1 hora, 49 minutos y 44.1 segundos'
    assert seconds_to_str(6950, language='es') == '1 hora, 55 minutos y 50 segundos'
    assert seconds_to_str(6950.13, language='es') == '1 hora, 55 minutos y 50.13 segundos'

    assert seconds_to_str(98798, language='es') == '1 día, 3 horas, 26 minutos y 38 segundos'
    assert seconds_to_str(98798.95, language='es') == '1 día, 3 horas, 26 minutos y 38.95 segundos'
    assert seconds_to_str(654233, language='es') == '7 días, 13 horas, 43 minutos y 53 segundos'
    assert seconds_to_str(654233.2, language='es') == '7 días, 13 horas, 43 minutos y 53.2 segundos'
    assert seconds_to_str(654984, language='es') == '7 días, 13 horas, 56 minutos y 24 segundos'
    assert seconds_to_str(654984.1, language='es') == '7 días, 13 horas, 56 minutos y 24.1 segundos'
    assert seconds_to_str(1989469, language='es') == '23 días, 37 minutos y 49 segundos'
    assert seconds_to_str(1989469.5, language='es') == '23 días, 37 minutos y 49.5 segundos'


def test_seconds_to_str_4():
    assert seconds_to_str(2.02, abbreviated=True) == '2.02 s'
    assert seconds_to_str(122.02, abbreviated=True) == '2 m and 2.02 s'
    assert seconds_to_str(7322.02, abbreviated=True) == '2 h, 2 m and 2.02 s'

    assert seconds_to_str(2.02, integer=True, abbreviated=True) == '2 s'
    assert seconds_to_str(122.02, integer=True, abbreviated=True) == '2 m and 2 s'
    assert seconds_to_str(7322.02, integer=True, abbreviated=True) == '2 h, 2 m and 2 s'

    assert seconds_to_str(3650, abbreviated=True) == '1 h and 50 s'
    assert seconds_to_str(3650.4, abbreviated=True) == '1 h and 50.4 s'
    assert seconds_to_str(86450, abbreviated=True) == '1 d and 50 s'
    assert seconds_to_str(86450.7, abbreviated=True) == '1 d and 50.7 s'

    assert seconds_to_str(356, abbreviated=True) == '5 m and 56 s'
    assert seconds_to_str(356.321, abbreviated=True) == '5 m and 56.32 s'
    assert seconds_to_str(635, abbreviated=True) == '10 m and 35 s'
    assert seconds_to_str(635.65, abbreviated=True) == '10 m and 35.65 s'
    assert seconds_to_str(6584, abbreviated=True) == '1 h, 49 m and 44 s'
    assert seconds_to_str(6584.1, abbreviated=True) == '1 h, 49 m and 44.1 s'
    assert seconds_to_str(6950, abbreviated=True) == '1 h, 55 m and 50 s'
    assert seconds_to_str(6950.13, abbreviated=True) == '1 h, 55 m and 50.13 s'

    assert seconds_to_str(98798, abbreviated=True) == '1 d, 3 h, 26 m and 38 s'
    assert seconds_to_str(98798.95, abbreviated=True) == '1 d, 3 h, 26 m and 38.95 s'
    assert seconds_to_str(654233, abbreviated=True) == '7 d, 13 h, 43 m and 53 s'
    assert seconds_to_str(654233.2, abbreviated=True) == '7 d, 13 h, 43 m and 53.2 s'
    assert seconds_to_str(654984, abbreviated=True) == '7 d, 13 h, 56 m and 24 s'
    assert seconds_to_str(654984.1, abbreviated=True) == '7 d, 13 h, 56 m and 24.1 s'
    assert seconds_to_str(1989469, abbreviated=True) == '23 d, 37 m and 49 s'
    assert seconds_to_str(1989469.5, abbreviated=True) == '23 d, 37 m and 49.5 s'


def test_seconds_to_str_5():
    assert seconds_to_str(2.02, language='es', abbreviated=True) == '2.02 s'
    assert seconds_to_str(122.02, language='es', abbreviated=True) == '2 m y 2.02 s'
    assert seconds_to_str(7322.02, language='es', abbreviated=True) == '2 h, 2 m y 2.02 s'

    assert seconds_to_str(2.02, integer=True, language='es', abbreviated=True) == '2 s'
    assert seconds_to_str(122.02, integer=True, language='es', abbreviated=True) == '2 m y 2 s'
    assert seconds_to_str(7322.02, integer=True, language='es',
                          abbreviated=True) == '2 h, 2 m y 2 s'

    assert seconds_to_str(3650, language='es', abbreviated=True) == '1 h y 50 s'
    assert seconds_to_str(3650.4, language='es', abbreviated=True) == '1 h y 50.4 s'
    assert seconds_to_str(86450, language='es', abbreviated=True) == '1 d y 50 s'
    assert seconds_to_str(86450.7, language='es', abbreviated=True) == '1 d y 50.7 s'

    assert seconds_to_str(356, language='es', abbreviated=True) == '5 m y 56 s'
    assert seconds_to_str(356.321, language='es', abbreviated=True) == '5 m y 56.32 s'
    assert seconds_to_str(635, language='es', abbreviated=True) == '10 m y 35 s'
    assert seconds_to_str(635.65, language='es', abbreviated=True) == '10 m y 35.65 s'
    assert seconds_to_str(6584, language='es', abbreviated=True) == '1 h, 49 m y 44 s'
    assert seconds_to_str(6584.1, language='es', abbreviated=True) == '1 h, 49 m y 44.1 s'
    assert seconds_to_str(6950, language='es', abbreviated=True) == '1 h, 55 m y 50 s'
    assert seconds_to_str(6950.13, language='es', abbreviated=True) == '1 h, 55 m y 50.13 s'

    assert seconds_to_str(98798, language='es', abbreviated=True) == '1 d, 3 h, 26 m y 38 s'
    assert seconds_to_str(98798.95, language='es', abbreviated=True) == '1 d, 3 h, 26 m y 38.95 s'
    assert seconds_to_str(654233, language='es', abbreviated=True) == '7 d, 13 h, 43 m y 53 s'
    assert seconds_to_str(654233.2, language='es', abbreviated=True) == '7 d, 13 h, 43 m y 53.2 s'
    assert seconds_to_str(654984, language='es', abbreviated=True) == '7 d, 13 h, 56 m y 24 s'
    assert seconds_to_str(654984.1, language='es', abbreviated=True) == '7 d, 13 h, 56 m y 24.1 s'
    assert seconds_to_str(1989469, language='es', abbreviated=True) == '23 d, 37 m y 49 s'
    assert seconds_to_str(1989469.5, language='es', abbreviated=True) == '23 d, 37 m y 49.5 s'
