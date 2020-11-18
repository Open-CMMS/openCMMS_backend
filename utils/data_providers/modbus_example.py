import socket

from umodbus import conf
from umodbus.client import tcp


def get_data(ip_address):
    conf.SIGNED_VALUES = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5002))
    value = tcp.read_holding_registers(1, 0, 1)
    sock.close()
    return value
