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
        handleConnection(connection, host, port)

def handleConnection(connection, host, port):
    clientRequest = connection.recv(1000)
    clientRequestType = clientRequest.splitlines()[0].split()[0]
    if clientRequestType == "GET":
        clientRequestPath = clientRequest.splitlines()[0].split()[1]
        serverResponse = ""
        if clientRequestPath == "/":
            serverResponse = getHomepageResponse(host, port)
        elif clientRequestPath == "/content":
            serverResponse = getContentResponse(host, port)
        elif clientRequestPath == "/file":
            serverResponse = getFileResponse(host, port)
        elif clientRequestPath == "/image":
            serverResponse = getImageResponse(host,port)
    elif clientRequestType == "POST":
        serverResponse = getPostResponse(host, port)

    connection.send(serverResponse)
    connection.close()

def getHomepageResponse(host, port):
    serverResponse = ""
    serverResponse += "HTTP/1.0 200 OK\r\n"
    serverResponse += "Content-type: text/html\r\n"
    serverResponse += "\r\n"
    serverResponse += "<h1>Home</h1>"
    serverResponse += "<p><a href=\"http://%s:%d/content\">Content</a></p>" % (host, port)
    serverResponse += "<p><a href=\"http://%s:%d/file\">File</a></p>" % (host, port)
    serverResponse += "<p><a href=\"http://%s:%d/image\">Image</a></p>" % (host, port)
    return serverResponse

def getContentResponse(host, port):
    serverResponse = ""
    serverResponse += "HTTP/1.0 200 OK\r\n"
    serverResponse += "Content-type: text/html\r\n"
    serverResponse += "\r\n"
    serverResponse += "<h1>Content Page</h1>"
    serverResponse += "<p><a href=\"http://%s:%d/\">Home</a></p>" % (host, port)
    return serverResponse

def getFileResponse(host, port):
    serverResponse = ""
    serverResponse += "HTTP/1.0 200 OK\r\n"
    serverResponse += "Content-type: text/html\r\n"
    serverResponse += "\r\n"
    serverResponse += "<h1>File Page</h1>"
    serverResponse += "<p><a href=\"http://%s:%d/\">Home</a></p>" % (host, port)
    return serverResponse

def getImageResponse(host, port):
    serverResponse = ""
    serverResponse += "HTTP/1.0 200 OK\r\n"
    serverResponse += "Content-type: text/html\r\n"
    serverResponse += "\r\n"
    serverResponse += "<h1>Image Page</h1>"
    serverResponse += "<p><a href=\"http://%s:%d/\">Home</a></p>" % (host, port)
    return serverResponse

def getPostResponse(host,port):
    serverResponse = "Hello, World."
    return serverResponse

if __name__ == '__main__':
    main()
