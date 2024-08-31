import socket
import select
import sys

address, max_clients = sys.argv[1:]

interface, port = address.rsplit(":", 1)
port = int(port)
address = interface, port
max_clients = int(max_clients)


def create_server():
    print(f"Ready to accept requests on {address}")
    return socket.create_server(address, backlog=1)


serv = create_server()
readers = {serv}
while True:
    ready, _, _ = select.select(readers, (), ())
    for client in ready:
        if client is serv:
            client, addr = serv.accept()
            readers.add(client)
            n = len(readers) - 1
            print(f"new client from {addr}. Now handling {n} clients")
            if n >= max_clients:
                print("Max clients reached. Disconnecting server")
                readers.remove(serv)
                serv.close()
                serv = None
            continue
        try:
            request = client.recv(1024)
            if not request:
                raise ConnectionError("client disconnected")
            client.sendall(request)
        except OSError as error:
            print(f"client error: {error!r}")
            client.close()
            readers.remove(client)
            if serv is None:
                serv = create_server()
                readers.add(serv)
