# server2.py
# multithreaded

import socket
from threading import Thread
from fib import fib

def fib_server(addr):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(addr)
  sock.listen(5)
  while True:
    client, addr = sock.accept()
    print('New connection from {0}'.format(addr))
    Thread(target=fib_handler, args=(client, addr)).start()

def fib_handler(client, addr):
  while True:
    req = client.recv(100)
    if not req:
      break
    n = int(req)
    result = fib(n)
    resp = str(result).encode('ascii') + b'\n'
    client.send(resp)
  print("Closed connection to {0}".format(addr))

fib_server(('', 25000))

