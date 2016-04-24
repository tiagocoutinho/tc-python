# perf2.py
# nb short request per second

import time
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('', 25000))

n = 0

from threading import Thread
def monitor():
  global n
  while True:
    time.sleep(1)
    print("{0} req/s".format(n))
    n = 0

th = Thread(target=monitor)
th.setDaemon(True)
th.start()

while True:
  sock.send(b'1')
  r = sock.recv(100)
  n += 1  
