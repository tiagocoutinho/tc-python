"""Simple socket with pre-fork model"""

import socket
import logging
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


def worker_loop(server, handler):
    wlog.info("ready to accept requests")
    try:
        while True:
            client, addr = server.accept()
            handler(client, addr)
    finally:
        wlog.info("thread graceful shutdown")


def worker_init():
    wlog.info("starting new worker thread...")


def worker_main(server, threads, log_level):
    config(log_level)
    wlog.info("starting worker...")
    try:
        with server:
            if threads:
                with multiprocessing.pool.ThreadPool(threads, worker_init) as pool:
                    def handler(*args):
                        pool.apply_async(handle_client, args)
                    worker_loop(server, handler)
            else:
                worker_loop(server, handle_client)
    except Exception as error:
        wlog.info("unhandled error: %r", error)
    except KeyboardInterrupt:
        wlog.info("ctrl-C pressed. Bailing out")
    finally:
        wlog.info("process graceful shutdown")


def master_main(addr, reuse_port, log_level, nb_threads):
    server = Server(addr, reuse_port=reuse_port)
    with server:
        try:
            worker_main(server, nb_threads, log_level)
        except KeyboardInterrupt:
            mlog.info("ctrl-C pressed. Bailing out")
        finally:
            mlog.info("master graceful shutdown")


def master_pre_fork(addr, reuse_port, log_level, nb_processes, nb_threads):
    ctx = multiprocessing.get_context("fork")
    server = Server(addr, reuse_port=reuse_port)
    pool = ctx.Pool(processes=nb_processes)
    with server, pool:
        args = server, nb_threads, log_level
        result = pool.starmap_async(worker_main, nb_processes*[args])
        result.wait()


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
