#!/usr/bin/env python
import random
import socket
import time
import urlparse
import cgi
import StringIO
import jinja2
import sys

# Set up the loader and environment
# for jinja2 templating engine
loader = jinja2.FileSystemLoader('./templates')
env = jinja2.Environment(loader=loader)

def handle_connection(conn):
    # Get the request and split it to get the
    # request type and the requested folder
    request_temp = ''
    while True:
        request_temp += conn.recv(1)
        if '\r\n\r\n' in request_temp:
            break

    request = StringIO.StringIO(request_temp)
    environ = {}

    environ['REQUEST_METHOD'], path, \
    environ['SERVER_PROTOCOL'] = request.readline().split()

    # Get the path information
    path = urlparse.urlparse(path)
    environ['PATH_INFO'] = path.path
    environ['QUERY_STRING'] = path.query

    # Get the query string information
    if environ['REQUEST_METHOD'] == 'GET':
        GetRequests(conn, environ, request)
    elif environ['REQUEST_METHOD'] == 'POST':
        PostRequests(conn, environ, request)
    else:
        error_500_not_implemented(conn, environ)

    conn.close()

def GetRequests(conn, environ, request):
    if environ['PATH_INFO'] == '/':
        send200(conn)
        index(conn, environ)
    elif environ['PATH_INFO'] == '/content':
        send200(conn)
        content_page(conn, environ)
    elif environ['PATH_INFO'] == '/file':
        send200(conn)
        file_page(conn, environ)
    elif environ['PATH_INFO'] == '/image':
        send200(conn)
        image_page(conn, environ)
    elif environ['PATH_INFO'] == '/form':
        send200(conn)
        form_page(conn, environ)
    elif environ['PATH_INFO'] == '/formpost':
        send200(conn)
        form_post_page(conn, environ)
    elif environ['PATH_INFO'] == '/submit':
        send200(conn)
        form_get_results_page(conn, environ)
    else:
        send404(conn)
        error_404(conn, environ)

def PostRequests(conn, environ, request):
    d = {}
    line = request.readline()
    while line != '\r\n':
        k, v = line.split(': ')
        d[k.lower()] = v.strip('\r\n')
        line = request.readline()

    if 'content-length' in d.keys():
        request = StringIO.StringIO(conn.recv(int(d['content-length'])))

    form = cgi.FieldStorage(headers=d, fp=request, environ=environ)

    if environ['PATH_INFO'] == '/submitpost':
        send200(conn)
        form_post_results_page(conn, form)
    else:
        send404(conn)
        error_404(conn, environ)

def send200(conn):
    conn.send('HTTP/1.0 200 OK\r\n')
    conn.send('Content-type: text/html\r\n')
    conn.send('\r\n')

def send404(conn):
    conn.send('HTTP/1.0 404 NOT FOUND\r\n')
    conn.send('Content-type: text/html\r\n')
    conn.send('\r\n')

def send501(conn):
    conn.send('HTTP/1.0 501 Not Implemented\r\n')
    conn.send('Content-type: text/html\r\n')
    conn.send('\r\n')

def index(conn, environ):
    conn.send(env.get_template('index.html').render())

def content_page(conn, environ):
    conn.send(env.get_template('content.html').render())

def file_page(conn, environ):
    conn.send(env.get_template('file.html').render())

def image_page(conn, environ):
    conn.send(env.get_template('image.html').render())

def form_page(conn, environ):
    conn.send(env.get_template('form.html').render())

def form_post_page(conn, environ):
    conn.send(env.get_template('form_post.html').render())

def form_get_results_page(conn, environ):
    query_string = urlparse.parse_qs(environ['QUERY_STRING'])
    vars = {'firstname':query_string['firstname'][0], 'lastname':query_string['lastname'][0]}

    conn.send(env.get_template('form_results.html').render(vars))

def form_post_results_page(conn, form):
    vars = {'firstname':form.getvalue('firstname'), 'lastname':form.getvalue('lastname')}
    
    conn.send(env.get_template('form_results.html').render(vars))

def error_404(conn, environ):
    conn.send(env.get_template('error404.html').render({'PATH': environ['PATH_INFO']}))


def error_500_not_implemented(conn, environ):
    send501(conn)
    conn.send(env.get_template('error500_not_implemented.html').render())

def main():
    s = socket.socket()         # Create a socket object
    host = socket.getfqdn() # Get local machine name
    port = random.randint(8000, 9999)
    # @btj: Replace 127.0.0.1 with host
    s.bind(('127.0.0.1', port))        # Bind to the port

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
