import socket

from umodbus import conf
from umodbus.client import tcp

from utils.data_provider import GetDataException


def get_data(ip_address):
    try:
        conf.SIGNED_VALUES = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_address, 5002))
        message = tcp.read_holding_registers(slave_id=1, starting_address=0, quantity=1)
        response = tcp.send_message(message, sock)
        sock.close()
        return response[0]
    except ConnectionRefusedError:
        raise GetDataException()
