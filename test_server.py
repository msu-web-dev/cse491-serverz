import sys
import server
import os

class AcceptCalledMultipleTimes(Exception):
    pass

class FakeArgParse(object):
    def __init__(self, obj, p=None):
        self.select_app = obj
        self.select_port = p
    def ArgumentParser(self, description=None):
        self.description=description
        return FakeArgParse(self.select_app, self.select_port)

    def add_argument(self, d, dest=None, nargs=None, choices=None, default=None, type=None):
        return

    def parse_args(self):
        class Temp(object):
            def __init__(self, arg2, arg1 = None):
                if arg1:
                    self.port = [arg1]
                else:
                    self.port = None
                self.app = [arg2]

        return Temp(self.select_app, self.select_port)

        

class FakeSocketModule(object):
    def getfqdn(self):
        return "fakehost"

    def socket(self):
        return FakeConnection("GET / HTTP/1.0\r\n\r\n")

class FakeConnection(object):
    """
    A fake connection class that mimics a real TCP socket for the purpose
    of testing socket I/O.
    """
    def __init__(self, to_recv):
        self.to_recv = to_recv
        self.sent = ""
        self.is_closed = False
        self.timeout = 0
        self.n_times_accept_called = 0

    def getsockname(self):
        return ("noclient", 32351)

    def bind(self, param):
        (host, port) = param

    def listen(self, n):
        assert n == 5
        if n != 5:
            raise Exception("n should be 5 you dummy")

    def accept(self):
        if self.n_times_accept_called >= 1:
            raise AcceptCalledMultipleTimes("stop calling accept, please")
        self.n_times_accept_called += 1

        c = FakeConnection("GET / HTTP/1.1\r\n\r\n")
        return c, ("noclient", 32351)

    def recv(self, n):
        if len(self.to_recv) == 0:
            raise Exception("timeout")
        if n > len(self.to_recv):
            r = self.to_recv
            self.to_recv = ""
            return r
            
        r, self.to_recv = self.to_recv[:n], self.to_recv[n:]
        return r
    def send(self, s):
        self.sent += s

    def sendall(self, s):
        self.sent += s

    def close(self):
        self.is_closed = True

    def settimeout(self, d):
        self.timeout = d

    def shutdown(self, d):
        self.shut = d

def getFakeModules(app, port=None):
    fakemodule = FakeSocketModule()
    fakeargparse = FakeArgParse(app, port)
    return fakemodule, fakeargparse
        
def test_main():
    fakemodule, fakeargparse = getFakeModules('myapp', 8888)
    success = False
    try:
        server.main(fakemodule, fakeargparse)
    except AcceptCalledMultipleTimes:
        success = True
        pass

    assert success, "something went wrong"

# Test a basic GET call.
def test_invalid_app():
    fakemodule, fakeargparse = getFakeModules('blah', 8888)
    success = False
    try:
        server.main(fakemodule, fakeargparse)
    except:
        success = True
        pass

    assert success, "something went wrong"

def test_auto_port():
    fakemodule, fakeargparse = getFakeModules('myapp')

    success = False
    try:
        server.main(fakemodule, fakeargparse)
    except AcceptCalledMultipleTimes:
        success = True
        pass

    assert success, "something went wrong"

def test_imageapp_select():
    fakemodule, fakeargparse = getFakeModules('image', 8888)
    success = False
    try:
        server.main(fakemodule, fakeargparse)
    except AcceptCalledMultipleTimes:
        success = True
        pass

    assert success, "something went wrong"

def test_chat_app():
    fakemodule, fakeargparse = getFakeModules('chat', 8888)
    success = False
    try:
        server.main(fakemodule, fakeargparse)
    except AcceptCalledMultipleTimes:
        success = True
        pass

    assert success, "something went wrong"


def test_quotes_app():
    fakemodule, fakeargparse = getFakeModules('quotes', 8888)
    success = False
    try:
        server.main(fakemodule, fakeargparse)
    except AcceptCalledMultipleTimes:
        success = True
        pass

    assert success, "something went wrong"

def test_handle_connection():
    serv = server.Server(8000)
    conn = FakeConnection("GET / HTTP/1.0\r\nUser-Agent: nosetests\r\n\r\n")

    serv.handle_connection(conn)

    assert 'HTTP/1.0 200 OK\r\n' in conn.sent, 'Got: %s' % (repr(conn.sent),)
    assert '<h1>Welcome to Brian\'s Web Server</h1>' in conn.sent, \
    'Got: %s' % (repr(conn.sent),)


def test_content():
    serv = server.Server(8000)
    conn = FakeConnection("GET /content HTTP/1.0\r\n\r\n")

    serv.handle_connection(conn)

    assert 'HTTP/1.0 200 OK\r\n' in conn.sent, 'Got: %s' % (repr(conn.sent),)
    assert '<h1>Content page!</h1>' in conn.sent, 'Got: %s' % (repr(conn.sent),)

def test_file():
    serv = server.Server(8000)
    conn = FakeConnection("GET /file HTTP/1.0\r\n\r\n")

    serv.handle_connection(conn)

    assert 'HTTP/1.0 200 OK\r\n' in conn.sent, 'Got: %s' % (repr(conn.sent),)
    assert '<iframe src="/file.txt" type="text/plain"></iframe>' in conn.sent, 'Got: %s' % (repr(conn.sent),)

def test_image():
    serv = server.Server(8000)
    conn = FakeConnection("GET /image HTTP/1.0\r\n\r\n")

    serv.handle_connection(conn)

    assert 'HTTP/1.0 200 OK\r\n' in conn.sent, 'Got: %s' % (repr(conn.sent),)
    assert '<img src="/img.jpg" />' in conn.sent, 'Got: %s' % (repr(conn.sent),)

def test_post():
    serv = server.Server(8000)
    conn = FakeConnection("POST / HTTP/1.0\r\n\r\n")

    serv.handle_connection(conn)

    assert 'HTTP/1.0 404 NOT FOUND\r\n' in conn.sent, 'Got: %s' % (repr(conn.sent),)
    assert '<h1>404 NOT FOUND</h1>' in conn.sent, 'Got: %s' % (repr(conn.sent),)

def test_form_get():

    serv = server.Server(8000)
    conn = FakeConnection("GET /submit?firstname=Brian&lastname=Jurgess HTTP/1.0\r\n\r\n")
    serv.handle_connection(conn)

    assert 'HTTP/1.0 200 OK\r\n' in conn.sent, 'Got: %s' % (repr(conn.sent),)
    assert 'Hello Brian Jurgess.' in conn.sent, 'Got: %s' % (repr(conn.sent),)

def test_form_post():
    serv = server.Server(8000)
    conn = FakeConnection("POST /submitpost HTTP/1.0\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 32\r\n\r\nfirstname=Brian&lastname=Jurgess")

    serv.handle_connection(conn)

    assert 'HTTP/1.0 200 OK\r\n' in conn.sent, 'Got: %s' % (repr(conn.sent),)
    assert 'Hello Brian Jurgess.' in conn.sent, 'Got: %s' % (repr(conn.sent),)

def test_form_page_get():
    serv = server.Server(8000)
    conn = FakeConnection("GET /form HTTP/1.0\r\n\r\n")

    serv.handle_connection(conn)

    assert 'HTTP/1.0 200 OK\r\n' in conn.sent, 'Got: %s' % (repr(conn.sent),)
    assert '<form action="/submit" method="GET">' in conn.sent, 'Got: %s' % (repr(conn.sent),)

def test_form_page_post():
    serv = server.Server(8000)
    conn = FakeConnection("GET /formpost HTTP/1.0\r\n\r\n")

    serv.handle_connection(conn)

    assert 'HTTP/1.0 200 OK\r\n' in conn.sent, 'Got: %s' % (repr(conn.sent),)
    assert '<form action="/submitpost" method="POST">' in conn.sent, 'Got: %s' % (repr(conn.sent),)

def test_501_error():
    serv = server.Server(8000)
    conn = FakeConnection("PATCH / HTTP/1.1\r\n\r\n")

    serv.handle_connection(conn)

    assert 'HTTP/1.0 501 NOT IMPLEMENTED\r\n' in conn.sent, 'Got: %s' % (repr(conn.sent),)
    assert '<h1>ERROR 501 NOT IMPLEMENTED</h1>' in conn.sent, 'Got: %s' % (repr(conn.sent),)

def test_404_error():
    serv = server.Server(8000)
    conn = FakeConnection("GET /blah HTTP/1.0\r\n\r\n")

    serv.handle_connection(conn)

    assert 'HTTP/1.0 404 NOT FOUND\r\n' in conn.sent, 'Got: %s' % (repr(conn.sent),)
    assert '<h1>404 NOT FOUND</h1>' in conn.sent, 'Got: %s' % (repr(conn.sent),)

def test_multipart_form():
    serv = server.Server(8000)
    request = 'POST / HTTP/1.0\r\nContent-type: multipart/form-data; boundary=aaaa\r\n\r\n' + \
              '--aaaa' + \
              '--aaaa'
    conn = FakeConnection(request)

    serv.handle_connection(conn)

    assert 'HTTP/1.0 404 NOT FOUND' in conn.sent, 'Got: %s' % (repr(conn.sent),)
    assert '<h1>404 NOT FOUND</h1>' in conn.sent, 'Got: %s' % (repr(conn.send),)

def test_jpg_serve():
    serv = server.Server(8000)
    conn = FakeConnection("GET /img.jpg HTTP/1.0\r\n\r\n")

    serv.handle_connection(conn)

    fp = open('./img.jpg', 'rb')
    d = fp.read()
    fp.close()

    assert d in conn.sent

def test_file_serve():
    serv = server.Server(8000)
    conn = FakeConnection("GET /file.txt HTTP/1.0\r\n\r\n")

    serv.handle_connection(conn)

    fp = open('./file.txt', 'rb')
    d = fp.read()
    fp.close()

    assert d in conn.sent

def test_non_existant_file():
    serv = server.Server(8000)
    conn = FakeConnection("GET /ddd.txt HTTP/1.0\r\n\r\n")

    serv.handle_connection(conn)

    assert 'HTTP/1.0 404 NOT FOUND' in conn.sent, 'Got: %s' % (repr(conn.sent),)
    assert '<h1>404 NOT FOUND</h1>' in conn.sent, 'Got: %s' % (repr(conn.sent),)
