import logging
import socket
import selectors
import sys

address, max_clients = sys.argv[1:]

interface, port = address.rsplit(":", 1)
port = int(port)
address = interface, port
max_clients = int(max_clients)


def create_server():
    logging.info(f"Ready to accept requests on {address}")
    sock = socket.create_server(address, backlog=1)
    sock.setblocking(False)
    return sock

logging.basicConfig(level="INFO", format="%(asctime)-15s: %(message)s")
select = selectors.DefaultSelector()
serv = create_server()
select.register(serv, selectors.EVENT_READ)
while True:
    events = select.select()
    for key, _ in events:
        client = key.fileobj
        if client is serv:
            client, addr = serv.accept()
            client.setblocking(False)
            select.register(client, selectors.EVENT_READ)
            n = len(select.get_map()) - 1
            logging.info(f"new client from {addr}. Now handling {n} clients")
            if n >= max_clients:
                logging.info("Max clients reached. Disconnecting server")
                select.unregister(serv)
                serv.close()
                serv = None
            continue
        try:
            request = client.recv(1024)
            logging.info(f"RECV: {request}")
            if not request:
                raise ConnectionError("client disconnected")
            client.sendall(request)
        except OSError as error:
            logging.info(f"client error: {error!r}")
            client.close()
            select.unregister(client)
            if serv is None:
                serv = create_server()
                select.register(serv, selectors.EVENT_READ)
