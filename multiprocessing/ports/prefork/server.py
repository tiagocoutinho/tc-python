"""Simple socket with pre-fork model"""

import sys
import time
import select
import socket
import logging
import threading
import multiprocessing.pool

import click


mlog = logging.getLogger("master")
wlog = logging.getLogger("worker")

STOP_MESSAGE = b"STOP\n"


exiting = False


def config(log_level):
    fmt = "%(asctime)s %(levelname)-9s %(processName)s/%(threadName)s/%(name)s %(message)s"
    logging.basicConfig(level=log_level, format=fmt)

    #logger = multiprocessing.get_logger()
    #logger.propagate = 1


def address(addr):
    host, port = addr.split(':', 1)
    return host, int(port)


def Server(addr, **kwargs):
    kwargs.setdefault("backlog", 5)
    server = socket.create_server(addr, **kwargs)
    #server.setblocking(False)
    return server


def handle_client(sock, addr):
    wlog.info("Handling client from %r", addr)
    with sock:
        try:
            while True:
                data = sock.recv(1024)
                if not data:
                    wlog.info("Client %r closed connection", addr)
                    return
                wlog.debug("req: %r", data)
                reply = data[::-1]
                sock.sendall(reply)
                wlog.debug("reply: %r", reply)
        except OSError as error:
            wlog.info("socket error from %r: %r", addr, error)


def accept(server):
    client, addr = server.accept()
    return handle_client(client, addr)


def worker_loop(server, channel):
    wlog.info("ready to accept requests")
    sockets = (server, channel)
    try:
        with server, channel:
            while True:
                socks, _, errors = select.select(sockets, (), sockets)
                if errors:
                    if channel in errors:
                        return
                    if channel in socks:
                        wlog.error("accept error. Exiting thread...")
                        break
                for sock in socks:
                    if sock is channel:
                        wlog.info("received stop signal")
                        if not channel.recv(1024):
                            return
                    elif sock is server:
                        try:
                            wlog.info("start accept")
                            accept(server)
                        except OSError as error:
                            wlog.warning("accept error: %r", error)
                            return
    finally:
        wlog.info("start thread graceful shutdown...")
        wlog.info("finished thread graceful shutdown")


def worker_main(server, threads, log_level, timeout=1):
    config(log_level)
    wlog.info("starting worker process...")
    with server:
        try:
            if threads:
                channels = []
                for i in range(threads):
                    s1, s2 = socket.socketpair()
                    s2.setblocking(False)
                    args = server, s2
                    thread = threading.Thread(
                        target=worker_loop,
                        args=args,
                        name=f"WorkerThread-{i:02d}"
                    )
                    channels.append((thread, s1))
                for thread, _ in channels:
                    thread.start()
                for thread, _ in channels:
                    thread.join()
            else:
                worker_loop(server, None)
        except Exception as error:
            wlog.info("unhandled error: %r", error)
        except KeyboardInterrupt:
            wlog.info("Ctrl-C pressed. Bailing out")
        finally:
            wlog.info("start worker process graceful shutdown...")
            if threads:
                for _, channel in channels:
                    channel.close()
                    #channel.sendall(STOP_MESSAGE)
                start = time.monotonic()
                for thread, _ in channels:
                    remaining = timeout - (time.monotonic() - start)
                    if remaining < 0:
                        wlog.warning("timeout waiting for worker threads")
                        sys.exit()
                    thread.join(remaining)
                if any(thread.is_alive() for thread, _ in channels):
                    wlog.warning("some worker threads are still alive")
                    sys.exit()
            wlog.info("finished worker process graceful shutdown")


def master_main(addr, reuse_port, log_level, nb_threads):
    with Server(addr, reuse_port=reuse_port) as server:
        try:
            worker_main(server, nb_threads, log_level)
        except KeyboardInterrupt:
            mlog.info("ctrl-C pressed. Bailing out")
        finally:
            mlog.info("start master graceful shutdown...")
            mlog.info("finished master graceful shutdown")


def master_pre_fork(addr, reuse_port, log_level, nb_processes, nb_threads):
    workers = []
    try:
        with Server(addr, reuse_port=reuse_port) as server:
            ctx = multiprocessing.get_context("fork")
            args = server, nb_threads, log_level
            workers = [
                ctx.Process(target=worker_main, args=args, name=f"WorkerProcess-{i:02d}")
                for i in range(nb_processes)
            ]

            [worker.start() for worker in workers]
            [worker.join() for worker in workers]
    except KeyboardInterrupt:
        mlog.info("Ctrl-C pressed. Bailing out")
    finally:
        mlog.info("start master graceful shutdown...")
        [worker.join() for worker in workers]
        mlog.info("finished master graceful shutdown")


@click.command()
@click.option('--listen', "addr", default=':5000', type=address, show_default=True)
@click.option('--log-level', default='INFO', type=str.upper, show_default=True)
@click.option('-p', '--processes', "nb_processes", default=0, show_default=True)
@click.option('-t', '--threads', "nb_threads", default=0, show_default=True)
@click.option("--reuse-port", is_flag=True)
def main(addr, log_level, nb_processes, nb_threads, reuse_port):
    config(log_level)
    if nb_processes:
        master_pre_fork(addr, reuse_port, log_level, nb_processes, nb_threads)
    else:
        master_main(addr, reuse_port, log_level, nb_threads)


if __name__ == "__main__":
    main()
