
# Testing data for seconds_to_str
# {(days, hours, minutes, seconds) : {(abbr, lang): result_expected}}

SECONDS_TO_STR_TEST_DATA = {
    (1, 1, 1, 1): {
        (False, "es"): "1 día, 1 hora, 1 minuto y 1 segundo",
        (False, "en"): "1 day, 1 hour, 1 minute and 1 second",
        (True, "es"): "1d, 1h, 1m y 1s",
        (True, "en"): "1d, 1h, 1m and 1s",
    },
    (1, 1, 1, 0): {
        (False, "es"): "1 día, 1 hora y 1 minuto",
        (False, "en"): "1 day, 1 hour and 1 minute",
        (True, "es"): "1d, 1h y 1m",
        (True, "en"): "1d, 1h and 1m",
    },
    (1, 1, 0, 1): {
        (False, "es"): "1 día, 1 hora y 1 segundo",
        (False, "en"): "1 day, 1 hour and 1 second",
        (True, "es"): "1d, 1h y 1s",
        (True, "en"): "1d, 1h and 1s",
    },
    (1, 1, 0, 0): {
        (False, "es"): "1 día y 1 hora",
        (False, "en"): "1 day and 1 hour",
        (True, "es"): "1d y 1h",
        (True, "en"): "1d and 1h",
    },
    (1, 0, 1, 1): {
        (False, "es"): "1 día, 1 minuto y 1 segundo",
        (False, "en"): "1 day, 1 minute and 1 second",
        (True, "es"): "1d, 1m y 1s",
        (True, "en"): "1d, 1m and 1s",
    },
    (1, 0, 1, 0): {
        (False, "es"): "1 día y 1 minuto",
        (False, "en"): "1 day and 1 minute",
        (True, "es"): "1d y 1m",
        (True, "en"): "1d and 1m",
    },
    (1, 0, 0, 1): {
        (False, "es"): "1 día y 1 segundo",
        (False, "en"): "1 day and 1 second",
        (True, "es"): "1d y 1s",
        (True, "en"): "1d and 1s",
    },
    (1, 0, 0, 0): {
        (False, "es"): "1 día",
        (False, "en"): "1 day",
        (True, "es"): "1d",
        (True, "en"): "1d",
    },
    (0, 1, 1, 1): {
        (False, "es"): "1 hora, 1 minuto y 1 segundo",
        (False, "en"): "1 hour, 1 minute and 1 second",
        (True, "es"): "1h, 1m y 1s",
        (True, "en"): "1h, 1m and 1s",
    },
    (0, 1, 1, 0): {
        (False, "es"): "1 hora y 1 minuto",
        (False, "en"): "1 hour and 1 minute",
        (True, "es"): "1h y 1m",
        (True, "en"): "1h and 1m",
    },
    (0, 1, 0, 1): {
        (False, "es"): "1 hora y 1 segundo",
        (False, "en"): "1 hour and 1 second",
        (True, "es"): "1h y 1s",
        (True, "en"): "1h and 1s",
    },
    (0, 1, 0, 0): {
        (False, "es"): "1 hora",
        (False, "en"): "1 hour",
        (True, "es"): "1h",
        (True, "en"): "1h",
    },
    (0, 0, 1, 1): {
        (False, "es"): "1 minuto y 1 segundo",
        (False, "en"): "1 minute and 1 second",
        (True, "es"): "1m y 1s",
        (True, "en"): "1m and 1s",
    },
    (0, 0, 1, 0): {
        (False, "es"): "1 minuto",
        (False, "en"): "1 minute",
        (True, "es"): "1m",
        (True, "en"): "1m",
    },
    (0, 0, 0, 1): {
        (False, "es"): "1 segundo",
        (False, "en"): "1 second",
        (True, "es"): "1s",
        (True, "en"): "1s",
    },
    (10, 20, 30, 40): {
        (False, "es"): "10 días, 20 horas, 30 minutos y 40 segundos",
        (False, "en"): "10 days, 20 hours, 30 minutes and 40 seconds",
        (True, "es"): "10d, 20h, 30m y 40s",
        (True, "en"): "10d, 20h, 30m and 40s",
    },
    (10, 20, 30, 0): {
        (False, "es"): "10 días, 20 horas y 30 minutos",
        (False, "en"): "10 days, 20 hours and 30 minutes",
        (True, "es"): "10d, 20h y 30m",
        (True, "en"): "10d, 20h and 30m",
    },
    (10, 20, 0, 40): {
        (False, "es"): "10 días, 20 horas y 40 segundos",
        (False, "en"): "10 days, 20 hours and 40 seconds",
        (True, "es"): "10d, 20h y 40s",
        (True, "en"): "10d, 20h and 40s",
    },
    (10, 20, 0, 0): {
        (False, "es"): "10 días y 20 horas",
        (False, "en"): "10 days and 20 hours",
        (True, "es"): "10d y 20h",
        (True, "en"): "10d and 20h",
    },
    (10, 0, 30, 40): {
        (False, "es"): "10 días, 30 minutos y 40 segundos",
        (False, "en"): "10 days, 30 minutes and 40 seconds",
        (True, "es"): "10d, 30m y 40s",
        (True, "en"): "10d, 30m and 40s",
    },
    (10, 0, 30, 0): {
        (False, "es"): "10 días y 30 minutos",
        (False, "en"): "10 days and 30 minutes",
        (True, "es"): "10d y 30m",
        (True, "en"): "10d and 30m",
    },
    (10, 0, 0, 40): {
        (False, "es"): "10 días y 40 segundos",
        (False, "en"): "10 days and 40 seconds",
        (True, "es"): "10d y 40s",
        (True, "en"): "10d and 40s",
    },
    (10, 0, 0, 0): {
        (False, "es"): "10 días",
        (False, "en"): "10 days",
        (True, "es"): "10d",
        (True, "en"): "10d",
    },
    (0, 20, 30, 40): {
        (False, "es"): "20 horas, 30 minutos y 40 segundos",
        (False, "en"): "20 hours, 30 minutes and 40 seconds",
        (True, "es"): "20h, 30m y 40s",
        (True, "en"): "20h, 30m and 40s",
    },
    (0, 20, 30, 0): {
        (False, "es"): "20 horas y 30 minutos",
        (False, "en"): "20 hours and 30 minutes",
        (True, "es"): "20h y 30m",
        (True, "en"): "20h and 30m",
    },
    (0, 20, 0, 40): {
        (False, "es"): "20 horas y 40 segundos",
        (False, "en"): "20 hours and 40 seconds",
        (True, "es"): "20h y 40s",
        (True, "en"): "20h and 40s",
    },
    (0, 20, 0, 0): {
        (False, "es"): "20 horas",
        (False, "en"): "20 hours",
        (True, "es"): "20h",
        (True, "en"): "20h",
    },
    (0, 0, 30, 40): {
        (False, "es"): "30 minutos y 40 segundos",
        (False, "en"): "30 minutes and 40 seconds",
        (True, "es"): "30m y 40s",
        (True, "en"): "30m and 40s",
    },
    (0, 0, 30, 0): {
        (False, "es"): "30 minutos",
        (False, "en"): "30 minutes",
        (True, "es"): "30m",
        (True, "en"): "30m",
    },
    (0, 0, 0, 40): {
        (False, "es"): "40 segundos",
        (False, "en"): "40 seconds",
        (True, "es"): "40s",
        (True, "en"): "40s",
    },
    (0, 0, 0, 0): {
        (False, "es"): "0 segundos",
        (False, "en"): "0 seconds",
        (True, "es"): "0s",
        (True, "en"): "0s",
    },
}

SPLIT_SECONDS_TEST_DATA = {}
