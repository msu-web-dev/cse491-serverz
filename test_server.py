import server
import requests

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

def testHandleConnectionHomepage():
    conn = FakeConnection("GET / HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' + \
                      '\r\n' + \
                      '<h1>Home</h1>' + \
                      '<p><a href=\"http://test:0/\">Home</a> | ' + \
                      '<a href=\"http://test:0/content\">Content</a> | ' + \
                      '<a href=\"http://test:0/file\">File</a> | ' + \
                      '<a href=\"http://test:0/image\">Image</a></p>' + \
                      '<p><form action=\'/submit\' method=\'GET\'>' + \
                      'Firstname: <input type=\'text\' name=\'firstname\'>' + \
                      '<br />' + \
                      'Lastname: <input type=\'text\' name=\'lastname\'>' + \
                      '<br />' + \
                      '<input type=\'submit\' value=\'submit\'>' + \
                      '</form></p>' + \
                      '<p><form action=\'/submit\' method=\'POST\'>' + \
                      'Firstname: <input type=\'text\' name=\'firstname\'>' + \
                      '<br />' + \
                      'Lastname: <input type=\'text\' name=\'lastname\'>' + \
                      '<br />' + \
                      '<input type=\'submit\' value=\'submit\'>' + \
                      '</form></p>'

    server.handleConnection(conn,"test",0)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def testHandleConnectionContent():
    conn = FakeConnection("GET /content HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' + \
                      '\r\n' + \
                      '<h1>Content</h1>' + \
                      '<p><a href=\"http://test:0/\">Home</a> | ' + \
                      '<a href=\"http://test:0/content\">Content</a> | ' + \
                      '<a href=\"http://test:0/file\">File</a> | ' + \
                      '<a href=\"http://test:0/image\">Image</a></p>'

    server.handleConnection(conn,"test",0)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def testHandleConnectionFile():
    conn = FakeConnection("GET /file HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' + \
                      '\r\n' + \
                      '<h1>File</h1>' + \
                      '<p><a href=\"http://test:0/\">Home</a> | ' + \
                      '<a href=\"http://test:0/content\">Content</a> | ' + \
                      '<a href=\"http://test:0/file\">File</a> | ' + \
                      '<a href=\"http://test:0/image\">Image</a></p>'

    server.handleConnection(conn,"test",0)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def testHandleConnectionImage():
    conn = FakeConnection("GET /image HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' + \
                      '\r\n' + \
                      '<h1>Image</h1>' + \
                      '<p><a href=\"http://test:0/\">Home</a> | ' + \
                      '<a href=\"http://test:0/content\">Content</a> | ' + \
                      '<a href=\"http://test:0/file\">File</a> | ' + \
                      '<a href=\"http://test:0/image\">Image</a></p>'

    server.handleConnection(conn,"test",0)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def testHandleConnectionFormSubmition():
    conn = FakeConnection("GET /submit?firstname=Doctor&lastname=Mario HTTP/1.0\r\n\r\n")
    expected_return = "HTTP/1.0 200 OK\r\n" + \
                      "Content-type: text/html\r\n" + \
                      "\r\n" + \
                      '<h1>Form Submition</h1>' + \
                      '<p><a href=\"http://test:0/\">Home</a> | ' + \
                      '<a href=\"http://test:0/content\">Content</a> | ' + \
                      '<a href=\"http://test:0/file\">File</a> | ' + \
                      '<a href=\"http://test:0/image\">Image</a></p>' + \
                      "<h2>Hello Doctor Mario.</h2>"
    
    server.handleConnection(conn,"test",0)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)
    
def testHandleConnectionPostFormSubmition():
    conn = FakeConnection("POST /submit HTTP/1.0\r\n\r\nfirstname=Doctor&lastname=Mario")
    expected_return = "HTTP/1.0 200 OK\r\n" + \
                      "Content-type: text/html\r\n" + \
                      "\r\n" + \
                      '<h1>Post Form Submition</h1>' + \
                      '<p><a href=\"http://test:0/\">Home</a> | ' + \
                      '<a href=\"http://test:0/content\">Content</a> | ' + \
                      '<a href=\"http://test:0/file\">File</a> | ' + \
                      '<a href=\"http://test:0/image\">Image</a></p>' + \
                      "<h2>Hello Doctor Mario.</h2>"
    
    server.handleConnection(conn,"test",0)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)    
    
def testHandleConnectionPost():
    conn = FakeConnection("POST / HTTP/1.0\r\n\r\n")
    expected_return = "HTTP/1.0 200 OK\r\n" + \
                      "Content-type: text/html\r\n" + \
                      '\r\n' + \
                      '<h1>Post</h1>' + \
                      '<p><a href=\"http://test:0/\">Home</a> | ' + \
                      '<a href=\"http://test:0/content\">Content</a> | ' + \
                      '<a href=\"http://test:0/file\">File</a> | ' + \
                      '<a href=\"http://test:0/image\">Image</a></p>' + \
                      'Hello Post World.'

    server.handleConnection(conn,"test",0)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)
