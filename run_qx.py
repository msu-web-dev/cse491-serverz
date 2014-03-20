import socket
import random

import time
from urlparse import urlparse
from StringIO import StringIO

### here is the code needed to create a WSGI application interface to
### a Quixote app:

#from app import make_app
import quixote
#from quixote.demo import create_publisher
#from quixote.demo.mini_demo import create_publisher
from quixote.demo.altdemo import create_publisher
#import imageapp


_the_app = None
def make_app():

    global _the_app

    if _the_app is None:
        #p = imageapp.create_publisher()
        p = create_publisher()
        _the_app = quixote.get_wsgi_app()
        #wsgi_app = make_app()

    return _the_app
### now that we have a WSGI app, we can run it in the WSGI reference server:

def handle_connection(c):
    req = c.recv(1)
    count = 0
    env = {}

    while req[-4:] != '\r\n\r\n':
        req += c.recv(1)

    req, data = req.split('\r\n', 1)
    headers = {}

    for line in data.split('\r\n')[:-2]:
        k,v = line.split(': ', 1)
        headers[k.lower()] = v

    path = urlparse(req.split(' ', 3)[1])
    env['REQUEST_METHOD'] = 'GET'
    env['PATH_INFO'] = path[2]
    env['QUERY_STRING'] = path[4]
    env['CONTENT_TYPE'] = 'text/html'
    env['CONTENT_LENGTH'] = 0
    env['SCRIPT_NAME'] = ''
    env['HTTP_COOKIE'] = headers['cookie'] if 'cookie' in headers.keys() else ''

    def start_response(status, response_headers):

        c.send('HTTP/1.0 ')
        c.send(status)
        c.send('\r\n')
        for pair in response_headers:
            key, header = pair
            c.send(key + ': ' + header + '\r\n')
        c.send('\r\n')


    content = ''

    if req.startswith('POST '):

        env['REQUEST_METHOD'] = 'POST'
        env['CONTENT_LENGTH'] = headers['content-length']
        env['CONTENT_TYPE'] = headers['content-type']
        print headers['content-length']


        while len(content) < int(headers['content-length']):

            content += c.recv(1)



    env['wsgi.input'] = StringIO(content)
    appl = make_app()
    result = appl(env, start_response)
    for data in result:
        c.send(data)

    c.close()

#from wsgiref.simple_server import make_server

def main():

    s = socket.socket()
    host = socket.getfqdn() # Get local machine name
    port = random.randint(8000, 9999)

    s.bind((host, port))

    print 'Starting server on', host, port
    print 'The Web server URL for this would be http://%s:%d/' % (host, port)

    s.listen(5)


    print 'Entering infinite loop; hit CTRL-C to exit'
    while True:

        c, (client_host, client_port) = s.accept()
        print 'Got connection from', client_host, client_port

        handle_connection(c)



if __name__ == '__main__':
    main()
    #p.is_thread_safe = True         # hack...
    #httpd = make_server('', port, wsgi_app)
    #print "Serving at http://%s:%d/.." % (host, port,)
    #httpd.serve_forever()


