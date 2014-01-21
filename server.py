#!/usr/bin/env python
import random
import socket
import time

s = socket.socket()
host = socket.getfqdn()
port = random.randint(8000, 9999)
s.bind((host, port))

print 'Starting server on', host, port
print 'The Web server URL for this would be http://%s:%d/' % (host, port)

s.listen(5)

print 'Entering infinite loop; hit CTRL-C to exit'
while True:
    c, (client_host, client_port) = s.accept()
    print c.recv(1000)
    print 'Got connection from', client_host, client_port

    c.send("HTTP/1.0 200 OK\r\n")
    c.send("Content-type: text/html\r\n")
    c.send("\r\n")
    c.send("<h1>Hello, World</h1>")
    c.send("This is msu-web-dev's Web server")
    c.close()
