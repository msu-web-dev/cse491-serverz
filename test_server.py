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

# Test basic GET calls.

# Test path = /
def test_handle_connection():
    conn = FakeConnection("GET / HTTP/1.0\r\n\r\n")

    server.handle_connection(conn, "arctic.cse.msu.edu", "9943")

    assert 'HTTP/1.0 200' in conn.sent and 'form' in conn.sent, \
    'Got: %s' % (repr(conn.sent),)

# Test path = /content
def test_handle_connection_content():
    conn = FakeConnection("GET /content HTTP/1.0\r\n\r\n")

    server.handle_connection(conn, "arctic.cse.msu.edu", "9943")

    assert 'HTTP/1.0 200' in conn.sent and 'content' in conn.sent, \
    'Got: %s' % (repr(conn.sent),)

# Test path = /file
def test_handle_connection_file():
    conn = FakeConnection("GET /file HTTP/1.0\r\n\r\n")

    server.handle_connection(conn, "arctic.cse.msu.edu", "9943")

    assert 'HTTP/1.0 200' in conn.sent and 'text/plain' in conn.sent, \
    'Got: %s' % (repr(conn.sent),)

# Test path = /content
def test_handle_connection_image():
    conn = FakeConnection("GET /image HTTP/1.0\r\n\r\n")

    server.handle_connection(conn, "arctic.cse.msu.edu", "9943")
    
    assert 'HTTP/1.0 200' in conn.sent and 'image/jpeg' in conn.sent, \
    'Got: %s' % (repr(conn.sent),)

# Test path = /submit
def test_handle_submit():
    conn = FakeConnection("GET /submit?firstname=Taylor&lastname=Swift" + \
                          " HTTP/1.1\r\n\r\n")

    server.handle_connection(conn, "arctic.cse.msu.edu", "9943")

    assert 'html' in conn.sent and "Taylor" in conn.sent \
      and 'Swift' in conn.sent, 'Got: %s' % (repr(conn.sent),)

# Test a submit with no first name
def test_handle_submit_no_first_name():
    conn = FakeConnection("GET /submit?firstname=&lastname=Swift" + \
                          " HTTP/1.1\r\n\r\n")

    server.handle_connection(conn, "arctic.cse.msu.edu", "9943")

    assert 'html' in conn.sent and "Swift" in conn.sent, \
    'Got: %s' % (repr(conn.sent),)

# Tests a submit with no last name
def test_handle_submit_no_last_name():
    conn = FakeConnection("GET /submit?firstname=Taylor&lastname=" + \
                          " HTTP/1.1\r\n\r\n")

    server.handle_connection(conn, "arctic.cse.msu.edu", "9943")

    assert 'html' in conn.sent and "Taylor" in conn.sent, \
    'Got: %s' % (repr(conn.sent),)

# test 404
def test_handle_not_found():
    conn = FakeConnection("GET /poop HTTP/1.0\r\n\r\n")

    server.handle_connection(conn, "arctic.cse.msu.edu", "9943")

    assert 'HTTP/1.0 404' in conn.sent and 'want' in conn.sent, \
    'Got: %s' % (repr(conn.sent),)

# Test POST connections

# Test / requests
def test_handle_connection_post():
    conn = FakeConnection("POST / HTTP/1.0\r\n" + \
      "Content-length: 0\r\n\r\n")

    server.handle_connection(conn, "arctic.cse.msu.edu", "9943")

    assert 'HTTP/1.0 200' in conn.sent and 'form' in conn.sent, \
    'Got: %s' % (repr(conn.sent),)

# Test /submit requests (both types)
def test_handle_submit_post():
    conn = FakeConnection("POST /submit HTTP/1.1\r\n" + \
                          "Content-Length: 31\r\n\r\n" + \
                          "firstname=Taylor&lastname=Swift")

    server.handle_connection(conn, "arctic.cse.msu.edu", "9943")
    
    assert 'HTTP/1.0 200' in conn.sent and "Hello Mrs." in conn.sent, \
    'Got: %s' % (repr(conn.sent),)
    
def test_handle_submit_post_multipart_and_form_data():
    conn = FakeConnection("POST /submit " + \
          "HTTP/1.1\r\nContent-length: 246\r\n\r\n------" + \
          "WebKitFormBoundaryAaal27xQakxMcNYm\r\n" + \
          'Content-Disposition: form-data; name="firstname"\r\n\r\nTaylor' + \
          '\r\n------WebKitFormBoundaryAaal27xQakxMcNYm\r\n' + \
          'Content-Disposition: form-data; name="lastname"\r\n\r\nSwift' + \
          '\r\n------WebKitFormBoundaryAaal27xQakxMcNYm--")')

    server.handle_connection(conn, "arctic.cse.msu.edu", "9943")
    
    assert 'HTTP/1.0 200' in conn.sent and "Hello Mrs." in conn.sent, \
    'Got: %s' % (repr(conn.sent),)

# test 404
def test_handle_not_found_post():
    conn = FakeConnection("POST /butts HTTP/1.1\r\n" + \
                          "Content-Length: 31\r\n\r\n" + \
                          "firstname=Taylor&lastname=Swift")

    server.handle_connection(conn, "arctic.cse.msu.edu", "9943")

    assert 'HTTP/1.0 404' in conn.sent and 'want' in conn.sent, \
    'Got: %s' % (repr(conn.sent),)

# Handle large request
def test_handle_long_request():
    firstname = lastname = "asdfasdfasdfasdfasdf" * 100
    conn = FakeConnection("POST /submit HTTP/1.1\r\n" + \
                          "Content-Length: 4020\r\n\r\n" + \
                          "firstname=%s&lastname=%s" % (firstname, lastname))

    server.handle_connection(conn, "arctic.cse.msu.edu", "9943")
    
    assert 'HTTP/1.0 200' in conn.sent and "Hello Mrs." in conn.sent, \
    'Got: %s' % (repr(conn.sent),)

# Test an empty request
def test_handle_empty_request():
  conn = FakeConnection("\r\n\r\n")

  server.handle_connection(conn, "arctic.cse.msu.edu", "9943")

  assert 'HTTP/1.0 404' in conn.sent and 'want' in conn.sent, \
    'Got: %s' % (repr(conn.sent),)