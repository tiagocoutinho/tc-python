"""
requirements:

$ pip install click

run with:
$ python tcp_proxy --listen=:5000 --connect=192.168.1.100:5000
"""

import socket
import select
import logging

import click


def address(addr):
    host, port = addr.split(':', 1)
    return host, int(port)


@click.command()
@click.option('--listen', default=('', 5000), type=address)
@click.option('--connect', type=address, help='ex: 192.168.1.100:5000')
@click.option('--log-level', default='INFO')
def main(listen, connect, log_level):
    logging.basicConfig(
        level=log_level, format="%(asctime)s:%(levelname)s:%(message)s"
    )
    serv = socket.socket()
    serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv.bind(listen)
    serv.listen(1)
    hardware = socket.create_connection(connect)
    socks = [serv, hardware]
    client = None
    try:
        while True:
            conns = socks + ([client] if client else [])
            readers, _, _ = select.select(conns, (), ())
            for reader in readers:
                if reader == serv:
                    sock, addr = reader.accept()
                    logging.info('NEW connection from %r', addr)
                    if client:
                        # don't accept more than one client (unpolite solution)
                        logging.info('REFUSE connection from %r', addr)
                        sock.close()
                    else:
                        client = sock
                elif reader is hardware:
                    data = reader.recv(2**12)
                    if data:
                        logging.info('HW -> CLIENT: %r', data)
                        if client:
                            client.sendall(data)
                        else:
                            logging.warning('Dropped HW -> CLIENT: %r', data)
                    else:
                        logging.error('Hardware disconnected!')
                        # we don't support reconnection, so just bail out
                        exit(1)
                else:  # must be a client socket
                    assert reader is client
                    data = client.recv(2**12)
                    if data:
                        logging.info('CLIENT -> HW: %r', data)
                        hardware.sendall(data)
                    else:
                        logging.info('CLIENT disconnected')
                        client = None
    finally:
        for sock in socks:
            if sock:
                print('close', sock)
                sock.close()


if __name__ == "__main__":
    main()
