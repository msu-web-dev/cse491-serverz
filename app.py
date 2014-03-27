# encoding: utf-8

import jinja2
from urlparse import parse_qs
import cgi
from os import listdir
from random import choice
from StringIO import StringIO

# Helper functions
def fileData(fname):
    fp = open(fname, 'rb')
    data = [fp.read()]
    fp.close()
    return data


def index(env, **kwargs):
    response_headers = [('Content-type', 'text/html; charset="UTF-8"')]
    
    template = env.get_template('index.html')
    data = [template.render(kwargs).encode('utf-8')]
    
    return (response_headers, data)

def content(env, **kwargs):
    response_headers = [('Content-type', 'text/html; charset="UTF-8"')]
    
    template = env.get_template('content.html')
    data = [template.render(kwargs).encode('utf-8')]
    
    return (response_headers, data)

def listImage(env, **kwargs):
    response_headers = [('Content-type', 'text/html; charset="UTF-8"')]

    kwargs['images'] = listdir('images')
    template = env.get_template('imagelist.html')
    data = [template.render(kwargs).encode('utf-8')]

    return (response_headers, data)

def serveImage(env, **kwargs):
    # Set our response headers to indicate an image
    response_headers = [('Content-type', 'image/jpeg')]

    # Load a random image from the images dir, and serve it
    data = fileData(kwargs['path'][1:])

    return (response_headers, data)

def serveFile(env, **kwargs):
    # Set our response headers to indicate plaintext
    response_headers = [('Content-type', 'text/plain; charset="UTF-8"')]

    # Load a random image from the images dir, and serve it
    data = fileData(kwargs['path'][1:])

    return (response_headers, data)

def File(env, **kwargs):
    # Load a random file from the files dir, and serve it
    kwargs['path'] = '/files/'+choice(listdir('files'))
    return serveFile(env, **kwargs)

def Image(env, **kwargs):
    # Load a random image from the images dir, and serve it
    kwargs['path'] = '/images/'+choice(listdir('images'))
    return serveFile(env, **kwargs)

def form(env, **kwargs):
    response_headers = [('Content-type', 'text/html; charset="UTF-8"')]

    template = env.get_template('form.html')
    data = [template.render(kwargs).encode('utf-8')]

    return (response_headers, data)

def submit(env, **kwargs):
    response_headers = [('Content-type', 'text/html; charset="UTF-8"')]
    
    template = env.get_template('submit.html')
    data = [template.render(kwargs).encode('utf-8')]
    
    return (response_headers, data)

def fail(env, **kwargs):
    response_headers = [('Content-type', 'text/html; charset="UTF-8"')]

    # Select an amusing image to acompany
    kwargs['img'] = './404/'+choice(listdir('404'))
    
    template = env.get_template('404.html')
    data = [template.render(kwargs).encode('utf-8')]
    
    return (response_headers, data)

def app(environ, start_response):
    """A simple WSGI application which serves several pages 
        and handles form data"""

    # The dict of pages we know how to serve, and their corresponding templates
    response = {
                '/'          : index,
                '/content'   : content,
                '/file'      : File,
                '/image'     : Image,
                '/imagelist' : listImage,
                '/form'      : form,
                '/submit'    : submit,
                '404'        : fail,
               }

    # Manually add all other available pages/images
    for page in listdir('404'):
        response['/404/' + page] = serveImage
    for page in listdir('images'):
        response['/images/' + page] = serveImage
    for page in listdir('files'):
        response['/files/' + page] = serveFile

    # Basic connection information and set up templates
    loader = jinja2.FileSystemLoader('./templates')
    env = jinja2.Environment(loader=loader)

    # Set up template arguments from GET requests
    qs = parse_qs(environ['QUERY_STRING']).iteritems()
    # Flatten the list we get from parse_qs; just assume we want the 0th for now
    args = {key : val[0] for key, val in qs}
    # Add the path to the args; we'll use this for page titles and 404s
    args['path'] = environ['PATH_INFO']

    # Grab POST args if there are any
    if environ['REQUEST_METHOD'] == 'POST':
        # Re-parse the headers into a format field storage can use
        # Dashes instead of underscores, all lowercased
        headers = { 
                    key[5:].lower().replace('_','-') : val
                    for key, val in environ.iteritems()
                    if(key.startswith('HTTP'))
                  }
        # Pull in the non-HTTP variables that field storage needs manually
        headers['content-type'] = environ['CONTENT_TYPE']
        headers['content-length'] = environ['CONTENT_LENGTH']
        # Create a field storage to process POST args

        ## Bad hack to get around validator problem
        if "multipart/form-data" in environ['CONTENT_TYPE']:
            cLen = int(environ['CONTENT_LENGTH'])
            data = environ['wsgi.input'].read(cLen)
            environ['wsgi.input'] = StringIO(data)

        fs = cgi.FieldStorage(fp=environ['wsgi.input'],
                                headers=headers, environ=environ)
        # Add these new args to the existing set
        args.update({key : fs[key].value for key in fs.keys()})

    # Get all the arguments in unicode form for Jinja
    args = {
            key.decode('utf-8') : val.decode('utf-8')
            for key, val in args.iteritems()
           }
    
    # Check if we got a path to an existing page
    if environ['PATH_INFO'] in response:
        # If we have that page, serve it with a 200 OK
        status = '200 OK'
        path = environ['PATH_INFO']
        
    else:
        # If we did not, redirect to the 404 page, with appropriate status
        status = '404 Not Found'
        path = '404'

    args['path'] = path
    response_headers, data = response[path](env, **args)

    # Return the page and status code
    # Page is first encoded to bytes from unicode for compatibility
    start_response(status, response_headers)
    return data

def make_app():
    """Wrapper function; returns the app function above to a WSGI server"""
    return app