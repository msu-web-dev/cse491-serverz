#!/usr/bin/env python
import random
import socket
import time
from urlparse import urlparse
from urlparse import parse_qs

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
    clientRequestPath = clientRequest.splitlines()[0].split()[1]
    urlDetails = urlparse(clientRequestPath)
    queryDictionary = parse_qs(urlDetails.query)
    clientRequestPath = urlDetails.path
    if clientRequestType == "GET":        
        serverResponse = ""
        if clientRequestPath == "/":
            serverResponse = buildHomepageResponse(host, port)
        elif clientRequestPath == "/content":
            serverResponse = buildContentResponse(host, port)
        elif clientRequestPath == "/file":
            serverResponse = buildFileResponse(host, port)
        elif clientRequestPath == "/image":
            serverResponse = buildImageResponse(host, port)
        elif clientRequestPath == "/submit":
	    serverResponse = \
            buildFormSubmitionResponse(host, port, queryDictionary)
    elif clientRequestType == "POST":
        if (clientRequestPath == "/submit"):
            serverResponse = \
            buildPostFormSubmitionResponse(host, port, clientRequest)
        else:
	    serverResponse = buildPostResponse(host, port)

    connection.send(serverResponse)
    connection.close()

def buildHttpHeader():
    return "HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n"

def buildHtmlBanner(pageName, host, port):
    return "<h1>%s</h1>" % (pageName) + \
           "<p><a href=\"http://%s:%s/\">Home</a> | " % (host, port) + \
           "<a href=\"http://%s:%s/content\">Content</a> | " % (host, port) + \
           "<a href=\"http://%s:%s/file\">File</a> | " % (host, port) + \
           "<a href=\"http://%s:%s/image\">Image</a></p>" % (host, port)

def buildNameForm(method):
    return "<form action='/submit' method='%s'>" % (method) + \
           "Firstname: <input type='text' name='firstname'><br />" + \
           "Lastname: <input type='text' name='lastname'><br />" + \
           "<input type='submit' value='submit'></form>"

def buildHomepageResponse(host, port):
    serverResponse = buildHttpHeader() + buildHtmlBanner("Home", host, port) + \
                     "<p>%s</p>" % (buildNameForm("GET")) + \
                     "<p>%s</p>" % (buildNameForm("POST"))
    return serverResponse

def buildContentResponse(host, port):
    serverResponse = buildHttpHeader() + buildHtmlBanner("Content", host, port)
    return serverResponse

def buildFileResponse(host, port):
    serverResponse = buildHttpHeader() + buildHtmlBanner("File", host, port)
    return serverResponse

def buildImageResponse(host, port):
    serverResponse = buildHttpHeader() + buildHtmlBanner("Image", host, port)
    return serverResponse
    
def buildFormSubmitionResponse(host, port, userInputQuery):
    try: 
        serverResponse = buildHttpHeader() + \
                         buildHtmlBanner("Form Submition", host, port) + \
                         "<h2>Hello %s %s.</h2>" % \
                         (userInputQuery['firstname'][0], \
                         userInputQuery['lastname'][0])
    except KeyError:
        serverResponse = buildHomepageResponse(host, port) + \
        "<h2>Please enter valid information.</h2>"
    return serverResponse

def buildPostResponse(host, port):
    serverResponse = buildHttpHeader() + buildHtmlBanner("Post", host, port) + \
                     "Hello Post World."
    return serverResponse

def buildPostFormSubmitionResponse(host, port, clientRequest):
    clientRequestPath = clientRequest.split()[-1]
    urlDetails = urlparse(clientRequestPath)
    userInputQuery = parse_qs(urlDetails.path)
    try:
        serverResponse = buildHttpHeader() + \
                         buildHtmlBanner("Post Form Submition", host, port) + \
                         "<h2>Hello %s %s.</h2>" % \
                         (userInputQuery['firstname'][0], \
                         userInputQuery['lastname'][0])
    except KeyError:
        serverResponse = buildHomepageResponse(host, port) + \
        "<h2>Please enter valid information.</h2>"
    return serverResponse    

if __name__ == '__main__':
    main()
