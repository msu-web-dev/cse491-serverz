from wsgiref.util import setup_testing_defaults
import StringIO
import jinja2
import urlparse
import cgi
import sys

# Set up the loader and environment
# for jinja2 templating engine
loader = jinja2.FileSystemLoader('./templates')
env = jinja2.Environment(loader=loader)


def hw5_app(environ, start_response):
	#setup_testing_defaults(environ)

	status = '200 OK'
	response_headers = [('Content-type', 'text/html')]
	response = ''
	if environ['REQUEST_METHOD'] == 'GET':
		status, response_headers, response = GetRequest(environ)
	elif environ['REQUEST_METHOD'] == 'POST':
		status, response_headers, response = PostRequest(environ)
	else:
		status, response_headers, response = error_501(environ)

	start_response(status, response_headers)
	return [response]

def GetRequest(environ):
    if environ['PATH_INFO'] == '/':
        return index(environ)
    elif environ['PATH_INFO'] == '/content':
        return content_page(environ)
    elif environ['PATH_INFO'] == '/file':
        return file_page(environ)
    elif environ['PATH_INFO'] == '/image':
        return image_page(environ)
    elif environ['PATH_INFO'] == '/form':
        return form_page(environ)
    elif environ['PATH_INFO'] == '/formpost':
        return form_post_page(environ)
    elif environ['PATH_INFO'] == '/submit':
        return form_get_results_page(environ)
    elif '.jpg' in environ['PATH_INFO'][-4:] or '.txt' in environ['PATH_INFO'][-4:]:
        return form_get_image(environ)
    else:
        return error_404(environ)

def PostRequest(environ):
	form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
	if environ['PATH_INFO'] == '/submitpost':
		return form_post_results_page(form)
	else:
		return error_404(environ)


def form_get_image(environ):
    try:
        fp = open('.%s' % environ['PATH_INFO'], 'rb')
    except:
        return error_404(environ)
    data = fp.read()
    fp.close()

    if '.txt' in environ['PATH_INFO'][-4:]:
        content_type = [('Content-type','text/plain')]
    else:
        content_type = [('Content-type','image/jpeg')]

    return '200 OK', content_type, data

def index(environ):
    return '200 OK', [('Content-type','text/html')], \
    env.get_template('index.html').render().encode('latin-1', 'replace')

def content_page(environ):
    return '200 OK', [('Content-type', 'text/html')], \
    env.get_template('content.html').render().encode('latin-1', 'replace')

def file_page(environ):
    return '200 OK', [('Content-type', 'text/html')], \
    env.get_template('file.html').render().encode('latin-1', 'replace')

def image_page(environ):
    return '200 OK', [('Content-type', 'text/html')], \
    env.get_template('image.html').render().encode('latin-1', 'replace')

def form_page(environ):
    return '200 OK', [('Content-type', 'text/html')], \
    env.get_template('form.html').render().encode('latin-1', 'replace')

def form_post_page(environ):
    return '200 OK', [('Content-type', 'text/html')], \
    env.get_template('form_post.html').render().encode('latin-1', 'replace')

def form_get_results_page(environ):
    query_string = urlparse.parse_qs(environ['QUERY_STRING'])
    query = {'firstname':query_string['firstname'][0], 'lastname':query_string['lastname'][0]}

    return '200 OK', [('Content-type', 'text/html')], \
    env.get_template('form_results.html').render(query).encode('latin-1', 'replace')

def form_post_results_page(form):
    query = {'firstname':form.getvalue('firstname'), 'lastname':form.getvalue('lastname')}
    
    return '200 OK', [('Content-type', 'text/html')], \
    env.get_template('form_results.html').render(query).encode('latin-1', 'replace')

def error_404(environ):
    return '404 NOT FOUND', [('Content-type', 'text/html')], \
    env.get_template('error404.html').render({'PATH': environ['PATH_INFO']}).encode('latin-1', 'replace')


def error_501(environ):
    return '501 NOT IMPLEMENTED', [('Content-type', 'text/html')], \
    env.get_template('error500_not_implemented.html').render().encode('latin-1', 'replace')

def make_app():
	return hw5_app
