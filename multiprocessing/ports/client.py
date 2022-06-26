import time
import socket
import operator
import functools
from concurrent.futures import wait, ThreadPoolExecutor, ProcessPoolExecutor

import click

def address(addr):
    host, port = addr.split(':', 1)
    return host, int(port)


def run_once(sock, data):
    start = time.monotonic()
    sock.sendall(data)
    sock.recv(8192)
    return time.monotonic() - start


def run(url, nb_loops, data):
    with socket.create_connection(url) as sock:
        func = functools.partial(run_once, sock, data)
        return functools.reduce(operator.add, (func() for _ in range(nb_loops)))


@click.command()
@click.option('--url', default='localhost:5000', type=address)
@click.option('--concurrency', default=1)
@click.option('--nb-calls', default=1)
@click.option('--executor', default="thread", type=click.Choice(["thread", "process"]))
@click.argument("data", type=str.encode)
def main(url, concurrency, nb_calls, executor, data):
    nb_iterations = nb_calls * concurrency
    Executor = ThreadPoolExecutor if executor == "thread" else ProcessPoolExecutor
    with Executor(max_workers=concurrency) as exe:
        # warm up to make sure all processes are created
        wait([exe.submit(time.sleep, 0) for _ in range(concurrency)])
        start = time.monotonic()
        futures = [exe.submit(run, url, nb_calls, data) for _ in range(concurrency)]
        values = sum(future.result() for future in futures)
        dt = time.monotonic() - start
    avg = values / nb_iterations
    total_avg = dt / nb_iterations
    print(f"Ran {nb_calls} in {concurrency} {executor}")
    print(f"Total calls: {nb_iterations} in {dt:.3f}s")
    print(f"Total nb. calls/s: {1/total_avg:.1f} ({total_avg*1E6:.2f}us per call)")
    print(f"Avg: {avg*1E6:.2f}us")
    print(f"Concurrency ratio: {avg / total_avg:.2f}")


if __name__ == "__main__":
    main()
