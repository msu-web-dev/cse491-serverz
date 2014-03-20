import server

class FakeConnection(object):
    """
    A fake connection class that mimics a real TCP socket for the purpose
    of testing socket I/O.
    """
    def __init__(self, to_recv):
        self.to_recv = to_recv
        self.sent = ""
        self.is_closed = False

    def recv(self, n):
        if n > len(self.to_recv):
            r = self.to_recv
            self.to_recv = ""
            return r
            
        r, self.to_recv = self.to_recv[:n], self.to_recv[n:]
        return r

    def send(self, s):
        self.sent += s

    def close(self):
        self.is_closed = True

# Test a basic GET call.

def test_handle_connection():
    conn = FakeConnection("GET / HTTP/1.0\r\n\r\n")



    server.handle_connection(conn)

    assert 'HTTP/1.0 200' in conn.sent and 'form' in conn.sent, \
            'Got: %s' % (repr(conn.sent),)

 
def test_handle_connection_post():
    conn = FakeConnection("POST / HTTP/1.0\r\n" + \
            "Content-Length: 0\r\n\r\n")

    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                        'Content-type: text/html\r\n' + \
                        '\r\n' + \
                        '<h1>Hello, world.</h1>' + \
                        'This is fenderic\'s Web server.<br>' + \
                        '<a href= /content>Content</a><br>' + \
                        '<a href= /file>File</a><br>' + \
                        '<a href= /image>Image</a><br>' + \
                        '<br> GET Form' + \
                        '<form action="/submit" method="GET">\n' + \
                        '<p>First Name: <input type="text" name="firstname"></p>\n' + \
                        '<p>Last Name: <input type="text" name="lastname"></p>\n' + \
                        '<input type="submit" value="Submit">\n\n' + \
                        '</form>' + \
                        '<br> POST Form' + \
                        '<form action="/submit" method="POST">\n' + \
                        '<p>First Name: <input type="text" name="firstname"></p>\n' + \
                        '<p>Last Name: <input type="text" name="lastname"></p>\n' + \
                        '<input type="submit" value="Submit">\n\n' + \
                        '</form>' + \
                        '<br> POST Form (multipart/form-data)' + \
                        '<form action="/submit" method="POST" enctype="multipart/form-data">\n' + \
                        '<p>First Name: <input type="text" name="firstname"></p>\n' + \
                        '<p>Last Name: <input type="text" name="lastname"></p>\n' + \
                        '<input type="submit" value="Submit">\n\n' + \
                        '</form>'



    server.handle_connection(conn)

    #assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)
    assert 'HTTP/1.0 200' in conn.sent and 'form' in conn.sent, \
            'GOT: %s' % (repr(conn.sent),)

def test_handle_connection_content():
    conn = FakeConnection("GET /content HTTP/1.0\r\n\r\n")

    server.handle_connection(conn)

    assert 'HTTP/1.0 200' in conn.sent and 'content' in conn.sent, \
            'Got: %s' % (repr(conn.sent),)
#
  
def test_handle_connection_file():
    conn = FakeConnection("GET /file HTTP/1.0\r\n\r\n")

    server.handle_connection(conn)

    assert 'HTTP/1.0 200' in conn.sent and 'file' in conn.sent, \
            'Got: %s' % (repr(conn.sent),)
#
   
def test_handle_connection_image():
    conn = FakeConnection("GET /image HTTP/1.0\r\n\r\n")

    server.handle_connection(conn)

    assert 'HTTP/1.0 200' in conn.sent and 'image' in conn.sent, \
            'Got: %s' % (repr(conn.sent),)
#

#def test_handle_connection_post():
#    conn = FakeConnection("POST / HTTP/1.0\r\n\r\n")
#    expected_return = 'HTTP/1.0 200 OK\r\n' + \
#                      'Content-type: text/html\r\n' + \
#                      '\r\n' + \
#                      'got a POST'
#
#    server.handle_connection(conn)
#
#    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_connection_submit():
    conn = FakeConnection("GET /submit?firstname=Eric&lastname=Austin HTTP/1.0\r\n\r\n")

    server.handle_connection(conn)

    assert 'html' in conn.sent and 'Eric' in conn.sent \
            and 'Austin' in conn.sent, 'Got: %s' % (repr(conn.sent),)
#

def test_handle_404():
    conn = FakeConnection("GET /bad HTTP/1.0\r\n\r\n")

    server.handle_connection(conn)

    assert 'HTTP/1.0 404' in conn.sent and 'lost' in conn.sent, \
            'Got: %s' % (repr(conn.sent),)

def test_handle_connection_submit_post():
    conn = FakeConnection("POST /submit HTTP/1.0\r\n" + \
            "Content-Length: 30\r\n\r\n" + \
            "firstname=Eric&lastname=Austin")

    server.handle_connection(conn)

    assert 'HTTP/1.0 200' in conn.sent and 'Hello' in conn.sent, \
            'Got: %s' % (repr(conn.sent),)
