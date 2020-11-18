import logging
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


@app.route(slave_ids=[1], function_codes=[1, 2], addresses=list(range(0, 10)))
def read_data_store(slave_id, function_code, address):
    """" Return value of address. """
    return data_store[address]


if __name__ == '__main__':
    try:
        print("Start server...")
        app.server_activate()
        print("Server online")
    finally:
        app.shutdown()
        print("\nStop server")
        app.server_close()
        print("Server offline")
