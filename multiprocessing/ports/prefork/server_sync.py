"""Simple socket with pre-fork model"""
import time
import signal
import socket
import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

import click


def config(log_level):
    fmt = "%(asctime)s %(levelname)s %(processName)s.%(threadName)s %(name)s %(message)s"
    logging.basicConfig(level=log_level.upper(), format=fmt)


def address(addr):
    host, port = addr.split(':', 1)
    return host, int(port)


def handle_client(sock, addr, log):
    log.info("Handling client from %r", addr)
    with sock:
        try:
            while True:
                data = sock.recv(1024)
                if not data:
                    log.info("Client %r closed connection", addr)
                    return
                log.debug("req: %r", data)
                reply = data[::-1]
                #time.sleep(0.001)
                sock.sendall(reply)
                log.debug("reply: %r", reply)
        except OSError as error:
            log.info("socket error from %r: %r", addr, error)


def worker_terminate(sig, ff):
    print("died", sig, ff)


def worker_main(server, threads, log_level):
    config(log_level)
    log = logging.getLogger(f"prefork.worker")
    log.info("starting...")
    signal.signal(signal.SIGTERM, worker_terminate)
    log.info("ready to handle requests!")
    try:
        if threads == -1:
            while True:
                client, addr = server.accept()
                handle_client(client, addr, log)
        else:
            with ThreadPoolExecutor(max_workers=threads, thread_name_prefix="TH") as exe:
                while True:
                    client, addr = server.accept()
                    exe.submit(handle_client, client, addr, log)
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
@click.option('-p', '--processes', "nb_processes", default=1, show_default=True)
@click.option('-t', '--threads', "nb_threads", default=-1, show_default=True)
def main(addr, log_level, nb_processes, nb_threads):
    config(log_level)
    log = logging.getLogger("prefork.supervisor")

    ctx = multiprocessing.get_context("spawn")

    log.info("start listening to %r", addr)
    server = socket.create_server(addr, reuse_port=False, backlog=5)
    log.info("bootstraping %d processes...", nb_processes)
    workers = [
        ctx.Process(target=worker_main, args=(server, nb_threads, log_level), name=f"W{i:03d}")
        for i in range(nb_processes)
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
