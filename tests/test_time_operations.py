from vcd.time_operations import seconds_to_str

def test_seconds_to_str():

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