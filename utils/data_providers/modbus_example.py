"""This file is an example for DataProvider python file."""

import socket

from umodbus import conf
from umodbus.client import tcp

from utils.data_provider import GetDataException


def get_data(ip_address, port=502):
    """get_data is excpected to return a unique value."""
    try:
        # Start of your code (example below)
        conf.SIGNED_VALUES = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_address, port))
        message = tcp.read_holding_registers(slave_id=1, starting_address=0, quantity=1)
        response = tcp.send_message(message, sock)
        sock.close()
        return response[0]
        # End of your code
    except ConnectionRefusedError as e:
        raise GetDataException(e)
    # Add exception if needed
