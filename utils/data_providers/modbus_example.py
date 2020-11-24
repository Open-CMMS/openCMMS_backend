import socket

from umodbus import conf
from umodbus.client import tcp

from utils.data_provider import GetDataException


def get_data(ip_address, port=502, memory_address=0, slave_id=1):
    """get_data is excpected to return a unique value."""
    try:
        conf.SIGNED_VALUES = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_address, 5002))
        message = tcp.read_holding_registers(slave_id=slave_id, starting_address=memory_address, quantity=1)
        response = tcp.send_message(message, sock)
        sock.close()
        return response[0]
    except ConnectionRefusedError:
        raise GetDataException()
