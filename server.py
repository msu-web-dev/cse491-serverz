#!/usr/bin/env python
import random
import socket
import time
import urlparse

def handle_connection(conn):
    # Get the request and split it to get the
    # request type and the requested folder
    request = conn.recv(1000).split('\n')
    request_type = request[0].split(' ')
    send200(conn)
    parsed_url = urlparse.urlparse(request_type[1]);
    if request_type[0] == 'GET':
        GetRequests(conn, parsed_url, request)
    elif request_type[0] == 'POST':
        PostRequests(conn, parsed_url, request)
    else:
        error_500_not_implemented(conn, parsed_url, request)

    conn.close()

def GetRequests(conn, parsed_url, request):
    if parsed_url.path == '/':
        index(conn, parsed_url, request)
    elif parsed_url.path == '/content':
        content_page(conn, parsed_url, request)
    elif parsed_url.path == '/file':
        file_page(conn, parsed_url, request)
    elif parsed_url.path == '/image':
        image_page(conn, parsed_url, request)
    elif parsed_url.path == '/form':
        form_page(conn, parsed_url, request)
    elif parsed_url.path == '/formpost':
        form_post_page(conn, parsed_url, request)
    elif parsed_url.path == '/submit':
        form_get_results_page(conn, parsed_url, request)
    else:
        error_404(conn, parsed_url, request)

def PostRequests(conn, parsed_url, request):
    if parsed_url.path == '/submitpost':
        form_post_results_page(conn, parsed_url, request)
    else:
        error_404(conn, parsed_url, request)

def send200(conn):
    conn.send('HTTP/1.0 200 OK\r\n')
    conn.send('Content-type: text/html\r\n')
    conn.send('\r\n')

def index(conn, parsed_url, request):
    conn.send('<html><body>')
    conn.send('<h1>Welcome to Brian\'s Web Server</h1>')
    conn.send('<div>')
    conn.send('<a href="/content">Content</a><br />')
    conn.send('<a href="/image">Image</a><br />')
    conn.send('<a href="/file">File</a><br />')
    conn.send('<a href="/form">Form Get</a><br />')
    conn.send('<a href="/formpost">Form Post</a><br />')
    conn.send('</div>')
    conn.send('</body></html>')

def content_page(conn, parsed_url, request):
    conn.send('<html><body>')
    conn.send('<h1>Content page!</h1>')
    conn.send('</body></html>')

def file_page(conn, parsed_url, request):
    conn.send('<html><body>')
    conn.send('<h1>File page!</h1>')
    conn.send('</body></html>')

def image_page(conn, parsed_url, request):
    conn.send('<html><body>')
    conn.send('<h1>Image page!</h1>')
    conn.send('</body></html>')

def form_page(conn, parsed_url, request):
    conn.send('<html><body>')
    conn.send('<form action="/submit" method="GET">')
    conn.send('<input type="text" name="firstname"/>')
    conn.send('<input type="text" name="lastname"/>')
    conn.send('<input type="submit" value="Submit" />')
    conn.send('</form></body></html>')

def form_post_page(conn, parsed_url, request):
    conn.send('<html><body>')
    conn.send('<form action="/submitpost" method="POST">')
    conn.send('<input type="text" name="firstname"/>')
    conn.send('<input type="text" name="lastname"/>')
    conn.send('<input type="submit" value="Submit"/>')
    conn.send('</form></body></html>')

def form_get_results_page(conn, parsed_url, request):
    query_string = urlparse.parse_qs(parsed_url.query)
    conn.send('<html><body>')
    conn.send('Hello %s %s.' % (query_string['firstname'][0], query_string['lastname'][0]))
    conn.send('</body></html>')

def form_post_results_page(conn, parsed_url, request):
    query_string = urlparse.parse_qs(request[-1])
    conn.send('<html><body>')
    conn.send('Hello %s %s.' % (query_string['firstname'][0], query_string['lastname'][0]))
    conn.send('</body></html>')

def error_404(conn, parsed_url, request):
    conn.send('<html><body>')
    conn.send('<h1>404 NOT FOUND</h1>')
    conn.send('<p>Could not find %s. Please try again.</p>' % parsed_url.path)
    conn.send('</body></html>')

def error_500_not_implemented(conn, parsed_url, request):
    conn.send('<html><body>')
    conn.send('<h1>ERROR 500 NOT IMPLEMENTED</h1>')
    conn.send('<p>This type of request has not been implemented.</p>')
    conn.send('</body></html>')

def main():
    s = socket.socket()         # Create a socket object
    host = socket.getfqdn() # Get local machine name
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
