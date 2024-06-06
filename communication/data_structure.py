import numpy as np
from ctypes import Structure, c_uint8, c_uint16, c_uint32, c_int32, c_int16, c_uint, c_int, cast, POINTER
from datetime import datetime, timezone
from typing import Optional
import ntplib


class Structure_SystemData(Structure):
    _pack_ = 1
    _fields_ = [
        ('cycle', c_uint16),
        ('serial', c_uint8 * 64),
        ('system_type', c_uint8),
        ('temp_range', c_uint8),
        ('memory_size', c_uint32),
        ('battery_soc', c_uint8),
        ('fw_version', c_uint8 * 3)
    ]


class Structure_Metadata(Structure):
    _pack_ = 1
    _fields_ = [
        ('start_time', c_uint32),
        ('reserved1', c_uint8 * 4),
        ('stop_time', c_uint32),
        ('records_count', c_uint32),
        ('stop_reason', c_uint8),
        ('reserved', c_uint8 * 7)
    ]


class Structure_Configuration(Structure):
    THR_DISABLED_VALUE = -32768
    TS_ILLEGAL_VALUE = 0xFFFFFFFF
    CONFIGURATION_MAGIC = 0x1066C01F
    CONFIGURATION_SIZE = 2048
    CONFIGURATION_VERSION = 0x01  # Initial version, FW version <= 0.100.N
    CONFIGURATION_VERSION_2 = 0x02  # Added consecutive and total alerts counters, FW version >= 0.101.0

    _pack_ = 1
    _fields_ = [
        ('magic', c_uint32),
        ('size', c_uint32),
        ('version', c_uint32),
        ('reserved1', c_uint32),
        ('meas_period', c_uint32),
        ('manual_delay', c_uint32),
        ('auto_delay', c_uint32),
        ('duration_time', c_uint32),
        ('max_records', c_uint32),
        ('description', c_uint8 * 256),
        ('timezone', c_int32),
        ('timezone_code', c_uint8 * 4),
        ('temp_unit', c_uint8),
        ('hum_enabled', c_uint8),
        ('als_enabled', c_uint8),
        ('stop_btn_enabled', c_uint8),
        ('date_fmt', c_uint8),
        ('time_fmt', c_uint8),
        ('hi_temp_thr', c_int16),
        ('lo_temp_thr', c_int16),
        ('hi_hum_thr', c_int16),
        ('lo_hum_thr', c_int16),
        ('alrt_cons', c_uint8),
        ('alrt_count', c_uint8),
        ('reserved2', c_uint8 * 68)
    ]

    @staticmethod
    def string_to_arr(string, array_size):
        unicode = string.encode('utf-8')
        return (c_uint8 * array_size)(*unicode[:array_size])

    @staticmethod
    def arr_to_string(arr):
        return bytes(arr).decode('utf-8', 'ignore')


class Structure_Records(Structure):
    _pack_ = 1
    _fields_ = [
        ('timestamp', c_uint32),
        ('temperature', c_int, 11),
        ('humidity', c_uint, 10),
        ('is_bookmark', c_uint, 1),
        ('is_tampered', c_uint, 1),
        ('reserved', c_uint, 9),
    ]


class Timestamp2020:
    TIMESTAMP_2020 = 1577836800

    @staticmethod
    def convert_to_datetime(timestamp) -> datetime:
        return datetime.utcfromtimestamp(timestamp + Timestamp2020.TIMESTAMP_2020)

    @staticmethod
    def convert_to_datetime_str(timestamp, date_fmt='%Y-%m-%d', time_fmt='%H:%M:%S') -> str:
        return datetime.utcfromtimestamp(timestamp + Timestamp2020.TIMESTAMP_2020).strftime(f'{date_fmt} {time_fmt}')

    @staticmethod
    def convert_to_timestamp(date, date_fmt='%Y-%m-%d') -> int:
        return int(datetime.strptime(date, date_fmt).replace(tzinfo=timezone.utc).timestamp()) - \
               Timestamp2020.TIMESTAMP_2020

    @staticmethod
    def get_local_utc_time() -> int:
        current_time = int(datetime.now(timezone.utc).timestamp()) - Timestamp2020.TIMESTAMP_2020
        if current_time < 0:
            current_time = 0
        return current_time

    @staticmethod
    def get_ntp_utc_time() -> Optional[int]:
        c = ntplib.NTPClient()
        try:
            response = c.request('0.pool.ntp.org')
            time = int(datetime.fromtimestamp(response.tx_time).timestamp()) - Timestamp2020.TIMESTAMP_2020
        except Exception as e:
            time = None
        return time

    @staticmethod
    def convert_to_duration_str(seconds) -> str:
        intervals = (
            ('days', 86400),
            ('hours', 3600),
            ('minutes', 60),
            ('seconds', 1)
        )
        result = []
        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value.__eq__(1):
                    name = name.rstrip('s')
                result.append(f'{value} {name}')
        result = ', '.join(result)
        return result if result else '0'


class DataEnums:
    temperature_unit_t = {
        0: 'Celsius',
        1: 'Fahrenheit'
    }
    date_format_t = {
        0: 'ISO (yyyy-mm-dd)',
        1: 'US (mm/dd/yyyy)',
        2: 'Europe (dd.mm.yyyy)'
    }
    date_format_mask = {
        0: '%Y-%m-%d',
        1: '%m/%d/%Y',
        2: '%d.%m.%Y'
    }
    time_format_t = {
        0: 'Europe (hh:mm:ss)',
        1: 'US (hh:mm:ss{AM|PM})',
    }
    time_format_mask = {
        0: '%H:%M:%S',
        1: '%I:%M:%S %p'
    }
    stop_reason_t = {
        0: 'Unknown',
        1: 'Stop button',
        2: 'Duration limit',
        3: 'Recordings limit',
        4: 'Memory limit',
        5: 'USB plug'
    }
    system_type_t = {
        1: 'Single use temperature logger',
        2: 'Single use temperature & humidity logger',
        3: 'Multiple use temperature & humidity logger'
    }
    temperature_range_t = {
        1: '-30..80',
        2: '-40..80',
        3: '-40..80'
    }
    product_codes_t = {
        1: 'T_SU',
        2: 'TH_SU',
        3: 'TH_MU'
    }

    @staticmethod
    def convert_celsius_to_required(temperature_celsius: float, required_unit: int) -> Optional[float]:
        if required_unit.__eq__(0):
            # Already Celsius
            return temperature_celsius
        elif required_unit.__eq__(1):
            # Convert to Fahrenheit
            return round((temperature_celsius * 9 / 5) + 32, 1)
        else:
            # Should never get here
            return None

    @staticmethod
    def convert_current_to_celsius(temperature_current: float, current_unit: int) -> Optional[float]:
        if current_unit.__eq__(0):
            # Already Celsius
            return temperature_current
        elif current_unit.__eq__(1):
            # Convert from Fahrenheit
            return round((temperature_current - 32) * 5 / 9, 1)
        else:
            # Should never get here
            return None


class Container_Recordings:

    def __init__(self):
        self.temperature = np.array([], dtype=float)
        self.humidity = np.array([], dtype=float)
        self.timestamp = np.array([], dtype=datetime)
        self.is_bookmark = np.array([], dtype=bool)
        self.is_tampered = np.array([], dtype=bool)

    def clear(self):
        self.temperature = np.delete(self.temperature, range(0, len(self.temperature)))
        self.humidity = np.delete(self.humidity, range(0, len(self.humidity)))
        self.timestamp = np.delete(self.timestamp, range(0, len(self.timestamp)))
        self.is_bookmark = np.delete(self.is_bookmark, range(0, len(self.is_bookmark)))
        self.is_tampered = np.delete(self.is_tampered, range(0, len(self.is_tampered)))

    def append(self, recording: Structure_Records, tz_offset: int, temp_unit: int):
        self.timestamp = np.append(self.timestamp, [Timestamp2020.convert_to_datetime(recording.timestamp + tz_offset)])
        self.temperature = np.append(self.temperature,
                                     DataEnums.convert_celsius_to_required(recording.temperature / 10,
                                                                           temp_unit))
        self.humidity = np.append(self.humidity, recording.humidity / 10)
        self.is_bookmark = np.append(self.is_bookmark, bool(recording.is_bookmark))
        self.is_tampered = np.append(self.is_tampered, bool(recording.is_tampered))
