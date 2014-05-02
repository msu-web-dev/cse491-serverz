# from http://docs.python.org/2/library/wsgiref.html

import cgi
import urlparse
import jinja2
from wsgiref.util import setup_testing_defaults
from StringIO import StringIO

def app(environ, start_response):
    loader = jinja2.FileSystemLoader('./templates')
    env = jinja2.Environment(loader=loader)

    # By default, set up the 404 page response. If it's
    # a valid page, we change this. If some weird stuff
    # happens, it'll default to 404.
    status = '404 Not Found'
    response_content = not_found('', env)
    headers = [('Content-type', 'text/html')]
    
    try:
        http_method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
    except:
        pass

    if http_method == 'POST':
        if path == '/':
            # I feel like there's a better way of doing this
            # than spamming status = '200 OK'. But it's almost 10
            # and we have to catch up because our capstone group
            # member just didn't do anything the past week. /rant
            status = '200 OK'
            response_content = handle_index(environ, env)
        elif path == '/submit':
            status = '200 OK'
            response_content = handle_submit_post(environ, env)
    elif http_method == 'GET':
        if path == '/':
            status = '200 OK'
            response_content = handle_index(environ, env)
        elif path == '/content':
            status = '200 OK'
            response_content = handle_content(environ, env)
        elif path == '/file':
            headers = [('Content-type', 'text/plain')]
            status = '200 OK'
            response_content = handle_file(environ, env)
        elif path == '/image':
            headers = [('Content-type', 'image/jpeg')]
            status = '200 OK'
            response_content = handle_image(environ, env)
        elif path == '/submit':
            status = '200 OK'
            response_content = handle_submit_get(environ, env)
                
    start_response(status, headers)
    response = []
    response.append(response_content)
    return response

def make_app():
    return app

def handle_index(params, env):
    return str(env.get_template("index_result.html").render())
    
def handle_content(params, env):
    return str(env.get_template("content_result.html").render())

def readFile(filepath):
    ''' Reads a file and returns its contents as a string '''
    f = open(filepath, 'rb')
    data = f.read()
    f.close()

    return data

def handle_file(params, env):
    return readFile('./files/butts.txt')

def handle_image(params, env):
    return readFile('./images/doge.jpeg')

def not_found(params, env):
    return str(env.get_template("not_found.html").render())

def handle_submit_post(environ, env):
    ''' Handle a connection given path /submit '''
    
    headers = {}
    for k in environ.keys():
        headers[k.lower()] = environ[k]

    headers['content-type'] = environ['CONTENT_TYPE']
    headers['content-length'] = environ['CONTENT_LENGTH']    

    firstNameFieldName = 'firstnamePOST2'
    lastNameFieldName = 'lastnamePOST2'

    # Kludgey workaround
    if "multipart/form-data" in environ['CONTENT_TYPE']:
        cLen = int(environ['CONTENT_LENGTH'])
        data = environ['wsgi.input'].read(cLen)
        environ['wsgi.input'] = StringIO(data)

        firstNameFieldName = 'firstnamePOST1'
        lastNameFieldName = 'lastnamePOST1'

    form = cgi.FieldStorage(headers = headers, fp = environ['wsgi.input'], 
                            environ = environ)

    try:
      firstname = form[firstNameFieldName].value
    except KeyError:
      firstname = ''

    try:
      lastname = form[lastNameFieldName].value
    except KeyError:
        lastname = ''

    vars = dict(firstname = firstname, lastname = lastname)
    return str(env.get_template("submit_result.html").render(vars))

def handle_submit_get(environ, env):
    ''' Handle a connection given path /submit '''
    # submit needs to know about the query field, so more
    # work needs to be done here.

    # we want the first element of the returned list
    params = environ['QUERY_STRING']
    params = urlparse.parse_qs(params)

    try:
      firstname = params['firstname'][0]
    except KeyError:
      firstname = ''
    try:
      lastname = params['lastname'][0]
    except KeyError:
      lastname = ''

    vars = dict(firstname = firstname, lastname = lastname)
    return str(env.get_template("submit_result.html").render(vars))
