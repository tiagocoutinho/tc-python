# perf1.py
# time of long request

import time
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('', 25000))

while True:
  s = time.time()
  sock.send(b'30')
  r = sock.recv(100)
  print(time.time()-s)
