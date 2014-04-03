import os
import sys
import time


class Recorder(object):
	def __init__(self, application):
		self.application = application

	def __call__(self, environ, start_response):
		f = open('TRAFFIC.log', 'a')
		f.write("="*70)
		f.write('\n')
		browser = environ['HTTP_USER_AGENT'] if 'HTTP_USER_AGENT' in environ.keys() else ''
		f.write("(SERVER) %s-- METHOD: %s,PATH: %s,BROWSER: %s" % (time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime()), \
			environ['REQUEST_METHOD'], environ['PATH_INFO'], browser))
		response = self.application(environ, start_response)
		response = "".join(response)
		f.write('\n')
		f.write("(APPLICATION) %s-- STATUS: %s" % (time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime()), start_response.status))
		f.write('\n')
		f.close()
		return [response]