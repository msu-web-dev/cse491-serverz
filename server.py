#!/usr/bin/env python
import random
import socket
import time
import urlparse
import StringIO
import sys
from app import make_app
import time
from wsgiref.validate import validator

# import quixote
# from quixote.demo import create_publisher
#from quixote.demo.mini_demo import create_publisher
#from quixote.demo.altdemo import create_publisher

# _the_app = None
# def make_app():
#     global _the_app
#     if _the_app is None:
#         p = create_publisher()
#         _the_app = quixote.get_wsgi_app()

#     return _the_app


def getRequest(conn):
    request = ''
    while True:
        request_temp = ''
        try:
            conn.settimeout(2)
            request_temp = conn.recv(2048)
        except:
            break
        request += request_temp
        if len(request_temp) < 2048:
            break
    return request


def createEnviron(conn):
    environ = {}
    environ['REQUEST_METHOD'] = ''
    environ['PATH_INFO'] = ''
    environ['SERVER_PROTOCOL'] = ''
    environ['SCRIPT_NAME'] = ''
    environ['wsgi.input'] = StringIO.StringIO('')
    environ['QUERY_STRING'] = ''
    environ['CONTENT_LENGTH'] = '0'
    environ['CONTENT_TYPE'] = 'text/html'
    environ['SERVER_NAME'] = ''
    environ['SERVER_PORT'] = ''
    environ['wsgi.version'] = ('',)
    environ['wsgi.errors'] = StringIO.StringIO()
    environ['wsgi.multithread'] = 0
    environ['wsgi.multiprocess'] = 0
    environ['wsgi.run_once'] = 0
    environ['wsgi.url_scheme'] = 'http'
    
    request = getRequest(conn)
    if request != '':
        request_headers, request_body = request.split('\r\n\r\n', 1)

        headers_string = ''
        request_line = 0
        try:
            request_line, headers_string = request_headers.split('\r\n', 1)
        except:
            request_line = request_headers
            headers_string = ''

        environ['REQUEST_METHOD'], PATH, \
        environ['SERVER_PROTOCOL'] = request_line.split(' ')

        PATH = urlparse.urlparse(PATH)

        environ['PATH_INFO'] = PATH.path
        environ['QUERY_STRING'] = PATH.query
        
        headers = []
        if headers_string != '':
            headers = headers_string.split('\r\n')

        headerDict = {}
        for line in headers:
            k, v = line.split(': ', 1)
            headerDict[k.lower()] = v

        if 'content-length' in headerDict.keys():
            environ['CONTENT_LENGTH'] = headerDict['content-length']
        
        environ['wsgi.input'] = StringIO.StringIO(request_body)

        if 'content-type' in headerDict.keys():
            environ['CONTENT_TYPE'] = headerDict['content-type']
        
            
    return environ






def handle_connection(conn):
    # Get the request and split it to get the
    # request type and the requested folder
    headers_set = []
    headers_sent = []

    def write(data):
        out = StringIO.StringIO()
        if not headers_set:
            raise AssertionError("write() called before start_response()")
        elif not headers_sent:
            status, response_headers = headers_sent[:] = headers_set
            out.write('HTTP/1.0 %s\r\n' % status)
            for header in response_headers:
                out.write('%s: %s\r\n' % header)
            out.write('\r\n')

        out.write(data)
        conn.send(out.getvalue())

    def start_response(status, response_headers, exc_info=None):
        if exc_info:
            try:
                if headers_sent:
                    print "here"
                    raise exc_info[1].with_traceback(exc_info[2])
            finally:
                exc_info = None
        elif headers_set:
            raise AssertionError("Headers already set!")

        headers_set[:] = [status, response_headers]
        headers_set[1].append(('Date', time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())))
        return write

    wsgi_app = make_app()
    environ = createEnviron(conn)
    result = wsgi_app(environ, start_response)

    try:
        for obj in result:
            if obj:
                write(obj)
        if not headers_sent:
            write('')
    finally:
        conn.close()

def main(socketmodule = None):
    if socketmodule is None:
        socketmodule = socket

    s = socketmodule.socket()         # Create a socket object
    host = socketmodule.getfqdn() # Get local machine name
    port = random.randint(8000, 9999)
    s.bind((host, port))        # Bind to the port

    print 'Starting server on', host, port
    print 'The Web server URL for this would be http://%s:%d/' % (host, port)

    s.listen(5)                 # Now wait for client connection.

    print 'Entering infinite loop; hit CTRL-C to exit'
    while True:
        # Establish connection with client.    
        c, (client_host, client_port) = s.accept()
        print 'Got connection from', client_host, client_port
        handle_connection(c)

if __name__ == '__main__':
    main()
