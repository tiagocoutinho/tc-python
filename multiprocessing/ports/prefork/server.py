"""Simple socket with pre-fork model"""

import socket
import logging
import multiprocessing.pool
from concurrent.futures import ThreadPoolExecutor

import click


log = logging.getLogger("server")
mlog = logging.getLogger("master")
wlog = log.getChild("worker")


def config(log_level):
    fmt = "%(asctime)s %(levelname)s %(processName)s.%(threadName)s %(name)s %(message)s"
    logging.basicConfig(level=log_level.upper(), format=fmt)


def address(addr):
    host, port = addr.split(':', 1)
    return host, int(port)


def Server(addr, **kwargs):
    kwargs.setdefault("backlog", 5)
    return socket.create_server(addr)


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
                #time.sleep(0.001)
                sock.sendall(reply)
                wlog.debug("reply: %r", reply)
        except OSError as error:
            wlog.info("socket error from %r: %r", addr, error)


def worker_loop(server):
    wlog.info("ready to accept requests")
    while True:
        handle_client(*server.accept())


def worker_main(server, threads, log_level):
    config(log_level)
    wlog.info("starting worker...")
    try:
        with server:
            if threads == -1:
                worker_loop(server)
            else:
                with ThreadPoolExecutor(max_workers=threads, thread_name_prefix="TH") as exe:
                    for _ in range(threads):
                        exe.submit(worker_loop, server)

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


def master_main(addr, log_level, nb_threads):
    log = logging.getLogger("master")
    server = Server(addr)
    with server:
        try:
            worker_main(server, nb_threads, log_level)
        except KeyboardInterrupt:
            log.info("ctrl-C pressed. Bailing out")
        finally:
            log.info("start master graceful shutdown!")
            log.info("finished master graceful shutdown")


def master_pre_fork(addr, log_level, nb_processes, nb_threads):
    log = logging.getLogger("master")
    ctx = multiprocessing.get_context("fork")
    server = Server(addr)
    pool = ctx.Pool(processes=nb_processes)
    with server, pool:
        args = server, nb_threads, log_level
        result = pool.starmap_async(worker_main, nb_processes*[args])
        result.wait()


@click.command()
@click.option('--listen', "addr", default=':5000', type=address, show_default=True)
@click.option('--log-level', default='INFO', show_default=True)
@click.option('-p', '--processes', "nb_processes", default=-1, show_default=True)
@click.option('-t', '--threads', "nb_threads", default=-1, show_default=True)
def main(addr, log_level, nb_processes, nb_threads):
    config(log_level)
    log = logging.getLogger("master")
    log.info("start listening to %r", addr)

    if nb_processes == -1:
        master_main(addr, log_level, nb_threads)
    else:
        master_pre_fork(addr, log_level, nb_processes, nb_threads)


if __name__ == "__main__":
    main()
