#!/usr/bin/env python

import sys
import os
import random
import socket
import urlparse
import StringIO
import argparse

import imageapp
from quotes import apps
from chat import apps as chatapp
from wsgiref.validate import validator

import quixote
from quixote.demo.altdemo import create_publisher

# Middleware
from middleware_components.wsgi_traffic_recording import Recorder

class StartResponse(object):
    def __call__(self, status, headers, exc_info=None):
        if exc_info:
            try:
                raise exc_info[1].with_traceback(exc_info[2])
            finally:
                exc_info=None
        self.status = status
        self.headers = headers

class Server(object):
    def __init__(self, port, wsgi_app=None, socketmodule=None):
        self.port = port
        if wsgi_app == None:
            wsgi_app = app.make_app()
        self.wsgi_app = wsgi_app
        self.socketmodule = socketmodule

    def obtain_request(self, conn):
        """ Obtains the request information from the socket """
        request = ''
        conn.settimeout(0.02)
        while True:
            try:
                request += conn.recv(4096)
            except:
                break

        return request



    def parse_request(self, request, conn):
        environ = {}
        environ['REQUEST_METHOD'] = ''
        environ['PATH_INFO'] = ''
        environ['SERVER_PROTOCOL'] = ''
        environ['QUERY_STRING'] = ''
        environ['wsgi.input'] = StringIO.StringIO('')
        environ['SCRIPT_NAME'] = ''
        environ['CONTENT_LENGTH'] = '0'
        environ['CONTENT_TYPE'] = 'text/html'
        environ['SERVER_NAME'] = "%s" % conn.getsockname()[0]
        environ['SERVER_PORT'] = "%s" % conn.getsockname()[1]
        environ['wsgi.version'] = (1,0)
        environ['wsgi.errors'] = sys.stderr
        environ['wsgi.multithread'] = 0
        environ['wsgi.multiprocess'] = 0
        environ['wsgi.run_once'] = 0
        environ['wsgi.url_scheme'] = 'http'
        if request != '':
            head, body = request.split('\r\n\r\n', 1)
            try:
                request_line, headers = head.split('\r\n', 1)
            except:
                request_line = head
                headers = ''

            request_type, path, protocol = request_line.split(' ')
            path = urlparse.urlparse(path)

            environ['REQUEST_METHOD'] = request_type
            environ['PATH_INFO'] = path.path
            environ['SERVER_PROTOCOL'] = protocol
            environ['QUERY_STRING'] = path.query
            environ['wsgi.input'] = StringIO.StringIO(body)
        
            if headers != '':
                headers = headers.split('\r\n')
                for line in headers:
                    k, v = line.split(': ', 1)
                    k = k.replace('-','_').upper()

                    if k == 'CONTENT_LENGTH':
                        environ['CONTENT_LENGTH'] = v
                    elif k == 'CONTENT_TYPE':
                        environ['CONTENT_TYPE'] = v
                    else:
                        environ['HTTP_%s' % k] = v
        return environ

    
    def handle_connection(self, conn):
        request = self.obtain_request(conn)
        environ = self.parse_request(request, conn)
        startresponse = StartResponse()

        # Uncomment to utilize the validator wsgi wrapper
        #self.wsgi_app = validator(self.wsgi_app(environ, startresponse))
        wsgi_app = Recorder(self.wsgi_app)
        result = wsgi_app(environ, startresponse)
        result = ''.join(result)
        headers = startresponse.headers

        print '%s -- %s -- %s' % (environ['REQUEST_METHOD'], environ['PATH_INFO'], startresponse.status)
        headers = '\r\n'.join([': '.join(x) for x in headers ])
        response = "HTTP/1.0 %s\r\n%s\r\n\r\n%s" % (startresponse.status, headers,result)
        conn.sendall(response)
        conn.shutdown(1)
        conn.close()

    def serve_forever(self):
        s = self.socketmodule.socket()
        host = self.socketmodule.getfqdn()
        s.bind((host,self.port))

        print "Starting server on:",host,self.port
        print "The server URL for this application is http://%s:%s/" % (host, self.port)

        s.listen(5)

        while True:
            c, (client_host, client_port) = s.accept()
            print '-----'
            print 'Receiving connection from: ', client_host, client_port

            self.handle_connection(c)

def main(socketmodule=None, argparsemodule=None):
    if socketmodule == None:
        socketmodule = socket

    if argparsemodule == None:
        argparsemodule = argparse

    parser = argparsemodule.ArgumentParser(description='Parse arguments for the app and port')
    parser.add_argument('-A', dest='app', nargs=1, \
        choices=['image','altdemo','myapp','django','quotes', 'chat'], default='image')
    parser.add_argument('-p', dest='port', nargs=1, type=int)
    args = parser.parse_args()

    if not args.port:
        port = random.randint(8000,9999)
    else:
        port = args.port[0]

    _selected_app = args.app[0]
    _the_app = None
    if _selected_app == 'image':
        imageapp.setup()
        p = imageapp.create_publisher()
        _the_app = quixote.get_wsgi_app()
    elif _selected_app == 'altdemo':
        p = create_publisher()
        _the_app = quixote.get_wsgi.app()
    elif _selected_app == 'myapp':
        _the_app = app.make_app()
    elif _selected_app == 'django':
        print "in here"
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imageappdjango.imageappdjango.settings-prod")
        from django.core.wsgi import get_wsgi_application
        sys.path.append(os.path.join(os.path.dirname(__file__), 'imageappdjango'))
        _the_app = get_wsgi_application()
    elif _selected_app == 'quotes':
        _the_app = apps.QuotesApp('quotes/quotes.txt', './quotes/html')
    elif _selected_app == 'chat':
        _the_app = chatapp.ChatApp('./chat/html')
    else:
        raise Exception("Invalid app selected")

    Server(port, _the_app, socketmodule).serve_forever()

if __name__ == '__main__':
    main()
    
