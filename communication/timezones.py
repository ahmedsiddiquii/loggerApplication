class Timezones:
    timezones_UTC = [
        'Local time zone',
        'UTC-12:00',
        'UTC-11:00',
        'UTC-10:00',
        'UTC-09:00',
        'UTC-08:00',
        'UTC-07:00',
        'UTC-06:00',
        'UTC-05:00',
        'UTC-04:00',
        'UTC-03:00',
        'UTC-02:00',
        'UTC-01:00',
        'UTC 00:00',
        'UTC+01:00',
        'UTC+02:00',
        'UTC+03:00',
        'UTC+04:00',
        'UTC+05:00',
        'UTC+06:00',
        'UTC+07:00',
        'UTC+08:00',
        'UTC+09:00',
        'UTC+10:00',
        'UTC+11:00',
        'UTC+12:00'
    ]

    timezones_GMT = [
        'Local time zone',
        'GMT-12:00',
        'GMT-11:00',
        'GMT-10:00',
        'GMT-09:00',
        'GMT-08:00',
        'GMT-07:00',
        'GMT-06:00',
        'GMT-05:00',
        'GMT-04:00',
        'GMT-03:00',
        'GMT-02:00',
        'GMT-01:00',
        'GMT 00:00',
        'GMT+01:00',
        'GMT+02:00',
        'GMT+03:00',
        'GMT+04:00',
        'GMT+05:00',
        'GMT+06:00',
        'GMT+07:00',
        'GMT+08:00',
        'GMT+09:00',
        'GMT+10:00',
        'GMT+11:00',
        'GMT+12:00'
    ]

    timezone_codes = [
        'GMT',
        'UTC'
    ]

    @staticmethod
    def get_zone_idx_by_offset(offset_secs):
        # We add additional 1 to avoid 'Local time zone' field
        return offset_secs // 3600 + 12 + 1
