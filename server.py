# Eric Austin - austine5 - fenderic

#!/usr/bin/env python
import random
import socket
import time
from urlparse import urlparse
from StringIO import StringIO
from wsgiref.validate import validator
from sys import stderr
import argparse

## My app.py
#from app import make_app
##

## Quixhote
#import quixote
#from quixote.demo.altdemo import create_publisher
#p = create_publisher()
##

## Image app
#import quixote
#import imageapp
#imageapp.setup()
#p = imageapp.create_publisher()
##

def handle_connection(conn, port, app):
#def handle_connection(conn, port):
    """Takes a socket connection, and serves a WSGI app over it.
        Connection is closed when app is served."""
    
    # Start reading in data from the connection
    req = conn.recv(1)
    count = 0
    env = {}
    while req[-4:] != '\r\n\r\n':
        new = conn.recv(1)
        if new == '':
            return
        else:
            req += new

    # Parse the headers we've received
    req, data = req.split('\r\n',1)
    headers = {}
    for line in data.split('\r\n')[:-2]:
        key, val = line.split(': ', 1)
        headers[key.lower()] = val

    # Parse the path and related env info
    urlInfo = urlparse(req.split(' ', 3)[1])
    env['REQUEST_METHOD'] = 'GET'
    env['PATH_INFO'] = urlInfo[2]
    env['QUERY_STRING'] = urlInfo[4]
    env['CONTENT_TYPE'] = 'text/html'
    env['CONTENT_LENGTH'] = str(0)
    env['SCRIPT_NAME'] = ''
    env['SERVER_NAME'] = socket.getfqdn()
    env['SERVER_PORT'] = str(port)
    env['wsgi.version'] = (1, 0)
    env['wsgi.errors'] = stderr
    env['wsgi.multithread']  = False
    env['wsgi.multiprocess'] = False
    env['wsgi.run_once']     = False
    env['wsgi.url_scheme'] = 'http'
    env['HTTP_COOKIE'] = headers['cookie'] if 'cookie' in headers.keys() else ''

    # Start response function for WSGI interface
    def start_response(status, response_headers):
        """Send the initial HTTP header, with status code 
            and any other provided headers"""
        
        # Send HTTP status
        conn.send('HTTP/1.0 ')
        conn.send(status)
        conn.send('\r\n')

        # Send the response headers
        for pair in response_headers:
            key, header = pair
            conn.send(key + ': ' + header + '\r\n')
        conn.send('\r\n')
    
    # If we received a POST request, collect the rest of the data
    content = ''
    if req.startswith('POST '):
        # Set up extra env variables
        env['REQUEST_METHOD'] = 'POST'
        env['CONTENT_LENGTH'] = str(headers['content-length'])
        env['CONTENT_TYPE'] = headers['content-type']
        # Continue receiving content up to content-length
        cLen = int(headers['content-length'])
        while len(content) < cLen:
            content += conn.recv(1)
        
    # Set up a StringIO to mimic stdin for the FieldStorage in the app
    env['wsgi.input'] = StringIO(content)
    
    # Get the application

    ## My app.py
    #wsgi_app = make_app()
    ## 
    
    ## Quixote alt.demo
    #wsgi_app = quixote.get_wsgi_app()
    ##

    ## Imageapp
    #wsgi_app = quixote.get_wsgi_app()
    ##

    if app == 'altdemo':

        import quixote
        from quixote.demo.altdemo import create_publisher
       
        try:
            p = create_publisher()
        except RuntimeError:
            pass

        wsgi_app = quixote.get_wsgi_app()

    elif app == 'image':

        import quixote
        import imageapp
        from imageapp import create_publisher

        try:
            p = create_publisher()
        except RuntimeError:
            pass

        imageapp.setup()
        wsgi_app = quixote.get_wsgi_app()

    elif app == 'myapp':

        from app import make_app

        wsgi_app = make_app()


    ## VALIDATION ##
    wsgi_app = validator(wsgi_app)
    ## VALIDATION ##

    result = wsgi_app(env, start_response)

    # Serve the processed data
    for data in result:
        conn.send(data)

    # Close the connection; we're done here
    result.close()
    conn.close()

def main():
    """Waits for a connection, then serves a WSGI app using handle_connection"""
    # Create a socket object
    sock = socket.socket()
    
    # Get local machine name (fully qualified domain name)
    host = socket.getfqdn()


    argParser = argparse.ArgumentParser(description='Set up WSGI server')
    argParser.add_argument('-A', metavar='App', type=str, nargs=1, \
            default='myapp', \
            choices=['myapp', 'image', 'altdemo'], \
            help='Select which app to run', dest='app')
    argParser.add_argument('-p', metavar='Port', type=int, nargs=1, \
            default=-1, help='Select a port to run on', \
            dest='p')
    argVals = argParser.parse_args()
    # Bind to a (random) port
    port = argVals.p[0] if argVals.p != -1 else random.randint(8000,9999)
    #port = random.randint(8000, 9999)
    #port = 8088

    sock.bind((host, port))

    print 'Starting server on', host, port
    print 'The Web server URL for this would be http://%s:%d/' % (host, port)

    # Now wait for client connection.
    sock.listen(5)

    print 'Entering infinite loop; hit CTRL-C to exit'
    # Whichever app we chose
    app = argVals.app[0]
    
    while True:
        # Establish connection with client.    
        conn, (client_host, client_port) = sock.accept()
        print 'Got connection from', client_host, client_port
        handle_connection(conn, port, app)
        
# boilerplate
if __name__ == "__main__":
    main()
