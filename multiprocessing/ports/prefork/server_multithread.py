"""Simple socket with pre-fork model"""
import signal
import socket
import logging
import multiprocessing

import click


def config(log_level):
    fmt = "%(asctime)s %(levelname)s %(processName)s.%(threadName)s %(name)s %(message)s"
    logging.basicConfig(level=log_level, format=fmt)


def address(addr):
    host, port = addr.split(':', 1)
    return host, int(port)


def handle_client(sock, addr, log):
    log.info("Handling client from %r", addr)
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                log.info("Client %r closed connection", addr)
                return
            log.info("req: %r", data)
            reply = data[::-1]
            sock.sendall(reply)
            log.info("reply: %r", reply)
    except OSError as error:
        log.info("socket error from %r: %r", addr, error)


def func(sig, ff):
    print("died", sig, ff)


def worker_main(server, name, log_level):
    config(log_level)
    log = logging.getLogger(f"prefork.worker.{name}")
    log.info("starting...")
    signal.signal(signal.SIGTERM, func)
    log.info("ready to handle requests!")
    try:
        while True:
            client, addr = server.accept()
            with client:
                handle_client(client, addr, log)
    except Exception as error:
        log.info("unhandled error: %r", error)
    except KeyboardInterrupt:
        log.info("ctrl-C pressed. Bailing out")
    finally:
        try:
            log.info("start worker graceful shutdown...")
            log.info("finished worker graceful shutdown")
        except BaseException as error:
            log.error("error in shutdown: %r", error)


@click.command()
@click.option('--listen', "addr", default=':5000', type=address, show_default=True)
@click.option('--log-level', default='INFO', show_default=True)
@click.option('--workers', "nb_workers", default=2, show_default=True)
def main(addr, log_level, nb_workers):
    config(log_level)
    log = logging.getLogger("prefork.supervisor")

    ctx = multiprocessing.get_context("spawn")

    log.info("start listening to %r", addr)
    server = socket.create_server(addr, reuse_port=False, backlog=5)
    log.info("bootstraping %d workers...", nb_workers)
    workers = [
        ctx.Process(target=worker_main, args=(server, f"{i:03d}", log_level), name=f"W{i:03d}")
        for i in range(nb_workers)
    ]
    log.info("ready to supervise workers")
    with server:
        try:
            [worker.start() for worker in workers]
            [worker.join() for worker in workers]
        except KeyboardInterrupt:
            log.info("ctrl-C pressed. Bailing out")
        finally:
            log.info("start master graceful shutdown!")
            [worker.join() for worker in workers]
#            [worker.terminate() for worker in workers]
            log.info("finished master graceful shutdown")


if __name__ == "__main__":
    main()
