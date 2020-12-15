"""This file emulate a modbus server for tests."""

import logging
import threading
import time
from collections import defaultdict
from socketserver import TCPServer

from umodbus import conf
from umodbus.server.tcp import RequestHandler, get_server
from umodbus.utils import log_to_stream

log_to_stream(level=logging.DEBUG)

data_store = defaultdict(int)
conf.SIGNED_VALUES = False

TCPServer.allow_reuse_address = True
app = get_server(TCPServer, ('localhost', 5002), RequestHandler)


@app.route(slave_ids=[1], function_codes=[1, 2, 3, 4], addresses=list(range(0, 10)))
def read_data_store(slave_id, function_code, address):
    """Return value of address."""
    return data_store[address]


@app.route(slave_ids=[1], function_codes=[5, 15], addresses=list(range(0, 10)))
def write_data_store(slave_id, function_code, address, value):
    """Set value for address."""
    data_store[address] = value


if __name__ == '__main__':
    try:
        print("Start server...")
        write_data_store(1, 6, 0, 0)
        t = threading.Thread(target=app.serve_forever)
        t.start()
        print("Server online")
        while True:
            time.sleep(60)
            write_data_store(1, 6, 0, read_data_store(1, 6, 0) + 1)
    finally:
        app.shutdown()
        print("\nStop server")
        app.server_close()
        print("Server offline")
