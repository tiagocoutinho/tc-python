import time
import socket
s = socket.socket()
s.connect(('', 25000))

# hide the cursor, clear screen, move cursor to 1,1
s.send(b'\x1b[?25l' b'\x1b[2J' b'\x1b[;H') 

# send hello
s.send(b'Hello, world!\n')

# send a progress bar
for i in range(1, 101):
  msg = "\r{0:>3}% [\x1b[32m{1:<50}\x1b[0m]".format(i, int(i/2)*"#")
  s.send(bytes(msg, 'ascii'))
  time.sleep(0.05)
s.send(b"\n")

# restore show cursor
s.send(b'\x1b[?25h')
