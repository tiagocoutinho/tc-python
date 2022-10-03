"""Simple socket with pre-fork model"""

import socket


def handle_client(sock, addr):
    print(f"Handling client from {addr}")
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                return
            sock.sendall(data[::-1])
    except OSError as error:
        print(f"socket error from {addr}: {error!r}")


def worker_main():
    addr = "0.0.0.0", 5000
    server = socket.create_server(addr, reuse_port=True, backlog=1)

    client, addr = server.accept()
    with client:
        handle_client(client, addr)


if __name__ == "__main__":
    worker_main()
