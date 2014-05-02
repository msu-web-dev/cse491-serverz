#!/usr/bin/env python
import random
import socket
import time
import urlparse
import os
import sys
import argparse
import imageapp
import quixote
import quixote.demo.altdemo
import app
import quotes
import chat
import cookieapp

from StringIO import StringIO

def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Server for several WSGI apps')
    parser.add_argument('-p', metavar='-p', type=int, nargs='?', default=-1,
                   help='an integer for the port number')

    parser.add_argument('-A', metavar='-A', type=str, nargs=1,
                   help='the app to run (image, altdemo, or myapp)')

    args = parser.parse_args()
    try:
      appname = args.A[0]
    except TypeError:
      appname = "HOLYSHITINVALIDAPPWTF"

    validApps = ['myapp', 'image', 'altdemo', 'quotes', 'chat', 'cookie']
    if appname not in validApps:
      raise Exception("Invalid application name. Please enter -A followed by 'myapp', " + 
        "'image', 'altdemo', 'quotes', 'cookie', or 'chat'")
    s = socket.socket()         # Create a socket object
    host = socket.getfqdn()     # Get local machine name
    port = args.p

    if port < 8000 or port > 9999:
      port = random.randint(8000,9999)


    s.bind((host, port))        # Bind to the port

    print 'Starting server on', host, port
    print 'The Web server URL for this would be http://%s:%d/' % (host, port)

    s.listen(5)                 # Now wait for client connection.

    print 'Entering infinite loop; hit CTRL-C to exit'
    while True:
        # Establish connection with client.    
        c, (client_host, client_port) = s.accept()
        print 'Got connection from', client_host, client_port, '\n'
        handle_connection(c, host, port, appname)

def handle_connection(conn, host, port, appname):
  environ = {}
  request = conn.recv(1)
  
  # This will get all the headers
  while request[-4:] != '\r\n\r\n':
    new = conn.recv(1)
    if new == '':
        return
    else:
        request += new

  request, data = request.split('\r\n',1)
  headers = {}
  for line in data.split('\r\n')[:-2]:
      key, val = line.split(': ', 1)
      headers[key.lower()] = val

  first_line_of_request_split = request.split('\r\n')[0].split(' ')

  # Path is the second element in the first line of the request
  # separated by whitespace. (Between GET and HTTP/1.1). GET/POST is first.
  http_method = first_line_of_request_split[0]
  environ['REQUEST_METHOD'] = first_line_of_request_split[0]

  try:
    parsed_url = urlparse.urlparse(first_line_of_request_split[1])
    environ['PATH_INFO'] = parsed_url[2]
    env['QUERY_STRING'] = parsed_url[4]
  except:
    pass

  urlInfo = urlparse.urlparse(request.split(' ', 3)[1])
  environ['REQUEST_METHOD'] = 'GET'
  environ['PATH_INFO'] = urlInfo[2]
  environ['QUERY_STRING'] = urlInfo[4]
  environ['CONTENT_TYPE'] = 'text/html'
  environ['CONTENT_LENGTH'] = str(0)
  environ['SCRIPT_NAME'] = ''
  environ['SERVER_NAME'] = socket.getfqdn()
  environ['SERVER_PORT'] = str(port)
  environ['wsgi.version'] = (1, 0)
  environ['wsgi.errors'] = sys.stderr
  environ['wsgi.multithread']  = False
  environ['wsgi.multiprocess'] = False
  environ['wsgi.run_once']     = False
  environ['wsgi.url_scheme'] = 'http'
  environ['HTTP_COOKIE'] = headers['cookie'] if 'cookie' in headers.keys() else ''

  def start_response(status, response_headers):
        conn.send('HTTP/1.0 ')
        conn.send(status)
        conn.send('\r\n')
        for pair in response_headers:
            key, header = pair
            conn.send(key + ': ' + header + '\r\n')
        conn.send('\r\n')

  content = ''
  if request.startswith('POST '):
      environ['REQUEST_METHOD'] = 'POST'
      environ['CONTENT_LENGTH'] = str(headers['content-length'])
      try:
        environ['CONTENT_TYPE'] = headers['content-type']
      except:
        pass

      cLen = int(headers['content-length'])
      while len(content) < cLen:
          content += conn.recv(1)
      
  environ['wsgi.input'] = StringIO(content)
  
  # Create the appropriate wsgi app based on the command-line parameter
  if appname == "image":
    try:
      # Sometimes this gets called multiple times. Blergh.
      p = imageapp.create_publisher()
      imageapp.setup()
    except RuntimeError:
      pass
  
    wsgi_app = quixote.get_wsgi_app()

  elif appname == "myapp":
    wsgi_app = app.make_app()
  elif appname == "altdemo":
    try:
      p = quixote.demo.altdemo.create_publisher()
    except RuntimeError:
      pass

    wsgi_app = quixote.get_wsgi_app()
  elif appname == "quotes":
    # The quotes files are in the 'quotes' subdirectory
    directory_path = './quotes/'
    wsgi_app = quotes.create_quotes_app(directory_path + 'quotes.txt', directory_path + 'html')

  elif appname == "chat":
    # The chat files are in the 'quotes' subdirectory
    wsgi_app = chat.create_chat_app('./chat/html')

  elif appname == "cookie":
    wsgi_app = cookieapp.wsgi_app

  result = wsgi_app(environ, start_response)
  try:
    for response in result:
      conn.send(response)
  finally:
    if hasattr(result, 'close'):
      result.close()
  conn.close()

if __name__ == '__main__':
   main()
