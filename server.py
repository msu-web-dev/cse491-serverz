#!/usr/bin/env python
import random
import socket
import time

def main():
    clientSocket = socket.socket()
    host = socket.getfqdn()
    port = random.randint(8000, 9999)
    clientSocket.bind((host, port))

    print 'The Web server URL for this would be http://%s:%d/' % (host, port)
    print 'Starting server on', host, port

    clientSocket.listen(5)

    print 'Entering infinite loop; hit CTRL-C to exit'
    while True:
    	connection, (client_host, client_port) = clientSocket.accept()
        print 'Got connection from', client_host, client_port
        HandleConnection(connection)

def HandleConnection(connection):
    connection.send("HTTP/1.0 200 OK\r\n")
    connection.send("Content-type: text/html\r\n")
    connection.send("\r\n")
    connection.send("<h1>Hello, World</h1>")
    connection.send("This is msu-web-dev's Web server")
    connection.close()

if __name__ == '__main__':
    main()
