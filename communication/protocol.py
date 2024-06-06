import serial.tools.list_ports
from communication.commands import Commands
from typing import Optional
from time import sleep
import numpy as np
import struct
from threading import Lock

HEADER_LENGTH = 8
SERIAL_BAUDRATE = 921600
READ_TIMEOUT = 1

CODE_NACK = b'\x15'
CODE_ACK = b'\x06'
CODE_NONE = b'\x00'


class Protocol:
    sync_sequence = b'HTLP'

    def __init__(self, com_port):
        self.sequence_number = 0
        self.mutex = Lock()
        self.serial_if = serial.Serial(port=com_port, baudrate=SERIAL_BAUDRATE, timeout=READ_TIMEOUT)
        if not self.serial_if.is_open:
            self.serial_if.open()
        print(f'Serial is open - {self.serial_if.is_open}')

    def __send_request(self, command: int, data: bytes = b''):
        self.serial_if.reset_input_buffer()
        self.serial_if.reset_output_buffer()
        packet = bytearray()
        packet += self.sync_sequence
        packet += len(data).to_bytes(length=2, byteorder='little')
        packet += self.sequence_number.to_bytes(length=1, byteorder='little')
        packet += command.to_bytes(length=1, byteorder='little')
        packet += data
        self.sequence_number = (self.sequence_number + 1) % 256
        packet_chunks = [packet[x:x + 64] for x in range(0, len(packet), 64)]
        for chunk in packet_chunks:
            self.serial_if.write(chunk)
            if len(packet_chunks) > 1:
                sleep(0.005)

    def __read_header(self) -> Optional[bytes]:
        header = self.serial_if.read(HEADER_LENGTH)
        if len(header).__ne__(HEADER_LENGTH):
            print('Header read timeout!')
            return None
        if header[0:4].__ne__(self.sync_sequence):
            print(f'Invalid sync sequence! - {header}')
            return None
        if header[6].__ne__(self.sequence_number):
            print('Wrong sequence number!')
            return None
        return header

    def __read_payload(self, size: int) -> Optional[bytes]:
        response = self.serial_if.read(size)
        if len(response).__ne__(size):
            print('Payload read timeout!')
            return None
        return response

    def __read_response(self) -> Optional[bytes]:
        header = self.__read_header()
        if header is None:
            return None
        payload_length = int.from_bytes(bytes=header[4:6], byteorder='little')
        payload = self.__read_payload(payload_length)
        if payload is None:
            return None
        if len(payload).__ne__(payload_length):
            print('Payload read timeout!')
            return None
        return payload

    def connect_to_device(self) -> bool:
        self.mutex.acquire()
        self.serial_if.timeout = 0.5
        self.__send_request(Commands.COMMAND_SYNC)
        response = self.__read_response()
        try:
            response_code = response[:1]
        except Exception as e:
            response_code = CODE_NONE
        self.serial_if.timeout = READ_TIMEOUT
        self.mutex.release()
        if response_code == CODE_ACK:
            return True
        return False

    def get_metadata(self) -> Optional[bytes]:
        self.mutex.acquire()
        self.__send_request(Commands.COMMAND_SEND_METADATA)
        response = self.__read_response()
        self.mutex.release()
        return response

    def get_system_data(self) -> Optional[bytes]:
        self.mutex.acquire()
        self.__send_request(Commands.COMMAND_SEND_SYSTEM_DATA)
        response = self.__read_response()
        self.mutex.release()
        return response

    def get_configuration(self) -> Optional[bytes]:
        self.mutex.acquire()
        self.__send_request(Commands.COMMAND_SEND_CONFIG)
        response = self.__read_response()
        self.mutex.release()
        return response

    def get_records_chunk(self, records_offset: int) -> Optional[bytes]:
        self.mutex.acquire()
        records_offset = struct.unpack('4B', struct.pack('I', records_offset))
        self.__send_request(Commands.COMMAND_SEND_RECORDS, data=bytes(records_offset))
        response = self.__read_response()
        self.mutex.release()
        return response

    def get_usb_label(self) -> Optional[bytes]:
        self.mutex.acquire()
        self.__send_request(Commands.COMMAND_SEND_USB_LABEL)
        response = self.__read_response()
        self.mutex.release()
        return response

    def send_configuration(self, configuration) -> bool:
        self.mutex.acquire()
        self.serial_if.timeout = 5
        self.__send_request(Commands.COMMAND_SAVE_CONFIG, data=bytearray(configuration))
        response = self.__read_response()
        try:
            response_code = response[:1]
        except Exception as e:
            response_code = CODE_NONE
        self.serial_if.timeout = READ_TIMEOUT
        self.mutex.release()
        if response_code == CODE_ACK:
            return True
        return False

    def send_current_time(self, current_time: int) -> bool:
        self.mutex.acquire()
        response_code = CODE_NONE
        if current_time is not None:
            current_time = struct.unpack('4B', struct.pack('I', current_time))
            self.__send_request(Commands.COMMAND_SAVE_CURRENT_TIME, data=bytes(current_time))
            response = self.__read_response()
            try:
                response_code = response[:1]
            except Exception as e:
                pass
        self.mutex.release()
        if response_code == CODE_ACK:
            return True
        return False

    def test_command(self) -> Optional[bytes]:
        self.__send_request(Commands.COMMAND_SEND_TEST_COMMAND, data=b'1')
        response = self.__read_response()
        return response

    def disconnect(self):
        self.serial_if.close()


class ProtocolExchangeException(Exception):

    def __init__(self, message='Error in data exchange'):
        super(ProtocolExchangeException, self).__init__(message)
