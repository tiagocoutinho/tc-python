"""Simple socket with pre-fork model"""

import select
import socket
import logging
import threading
import multiprocessing.pool

import click


mlog = logging.getLogger("master")
wlog = logging.getLogger("worker")


def config(log_level):
    fmt = "%(asctime)s %(levelname)-5s %(processName)s/%(threadName)s/%(name)s %(message)s"
    logging.basicConfig(level=log_level, format=fmt)

    #logger = multiprocessing.get_logger()
    #logger.propagate = 1


def address(addr):
    host, port = addr.split(':', 1)
    return host, int(port)


def Server(addr, **kwargs):
    kwargs.setdefault("backlog", 5)
    return socket.create_server(addr, **kwargs)


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


def worker_loop(server, channel):
    wlog.info("ready to accept requests")
    try:
        with server, channel:
            while True:
                socks, _, _ = select.select((server, channel), (), ())
                for sock in socks:
                    if sock is channel:
                        wlog.info("received stop signal")
                        assert channel.recv(1024) == b"STOP\n"
                        return
                    elif sock is server:
                        try:
                            client, addr = server.accept()
                            handle_client(client, addr)
                        except OSError as error:
                            wlog.warning("accept error: %r", error)
                            return
    finally:
        wlog.info("thread graceful shutdown")


def worker_main(server, threads, log_level):
    config(log_level)
    wlog.info("starting worker process...")
    try:
        with server:
            if threads:
                channels = []
                for i in range(threads):
                    s1, s2 = socket.socketpair()
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
        wlog.info("start worker process graceful shutdown")
        server.close()
        if threads:
            for _, channel in channels:
                channel.sendall(b"STOP\n")
            for thread, _ in channels:
                thread.join()


def master_main(addr, reuse_port, log_level, nb_threads):
    with Server(addr, reuse_port=reuse_port) as server:
        try:
            worker_main(server, nb_threads, log_level)
        except KeyboardInterrupt:
            mlog.info("ctrl-C pressed. Bailing out")
        finally:
            mlog.info("master graceful shutdown")


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
