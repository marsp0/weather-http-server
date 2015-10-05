from SocketServer import *
import requests
import os

class WeatherRequestHandler(StreamRequestHandler):

	#copied from the SimpleHTTPServer because LAZY lel
	http_version = 'HTTP/1.1'
	responses = {
        100: ('Continue', 'Request received, please continue'),
        101: ('Switching Protocols',
              'Switching to new protocol; obey Upgrade header'),

        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted',
              'Request accepted, processing continues off-line'),
        203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
        204: ('No Content', 'Request fulfilled, nothing follows'),
        205: ('Reset Content', 'Clear input form for further input.'),
        206: ('Partial Content', 'Partial content follows.'),

        300: ('Multiple Choices',
              'Object has several resources -- see URI list'),
        301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('See Other', 'Object moved -- see Method and URL list'),
        304: ('Not Modified',
              'Document has not changed since given time'),
        305: ('Use Proxy',
              'You must use proxy specified in Location to access this '
              'resource.'),
        307: ('Temporary Redirect',
              'Object moved temporarily -- see URI list'),

        400: ('Bad Request',
              'Bad request syntax or unsupported method'),
        401: ('Unauthorized',
              'No permission -- see authorization schemes'),
        402: ('Payment Required',
              'No payment -- see charging schemes'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
              'Specified method is invalid for this resource.'),
        406: ('Not Acceptable', 'URI not available in preferred format.'),
        407: ('Proxy Authentication Required', 'You must authenticate with '
              'this proxy before proceeding.'),
        408: ('Request Timeout', 'Request timed out; try again later.'),
        409: ('Conflict', 'Request conflict.'),
        410: ('Gone',
              'URI no longer exists and has been permanently removed.'),
        411: ('Length Required', 'Client must specify Content-Length.'),
        412: ('Precondition Failed', 'Precondition in headers is false.'),
        413: ('Request Entity Too Large', 'Entity is too large.'),
        414: ('Request-URI Too Long', 'URI is too long.'),
        415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
        416: ('Requested Range Not Satisfiable',
              'Cannot satisfy request range.'),
        417: ('Expectation Failed',
              'Expect condition could not be satisfied.'),

        500: ('Internal Server Error', 'Server got itself in trouble'),
        501: ('Not Implemented',
              'Server does not support this operation'),
        502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
        503: ('Service Unavailable',
              'The server cannot process the request due to a high load'),
        504: ('Gateway Timeout',
              'The gateway server did not receive a timely response'),
        505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
        }

	error_message = '''
	<html>
		<head>						
			<title>{title}</title>
		<head>
		<body>
			<h1>{code} {explanation}</h1>
		</body>
	</html>
	'''

	def handle(self):
		#we read the first line of the the request and split it
		request_list = self.rfile.readline().split()
		#we check if the path/command/version are in the list
		if len(request_list) == 3:
			self.command, self.path, self.version = request_list
			if self.version[:5] != 'HTTP/' or self.command not in ('GET', 'POST'):
				self.send_error(400)
			self.headers = self.get_headers()
			method = getattr(self,self.command.lower())
			method()
		#if its version 0.9, we deny because this version doesn't support post, so no need for them to use the site
		elif len(request_list) == 2: 
			self.send_error(505)
		#block everything else (is it a good idea ?)
		else:
			self.send_error(400)

	def get_headers(self):
		''' function to get all the headers from the stream and to make a dict from the string.
			Note : how are items in the headers split ?
		'''
		#prepare the str for the headers
		headers = ''
		#create the temp dict that we are going to return
		temp_dict = {}
		#prepare the checking value
		requestline = ''
		#get everything before the \r\n - universal sign that the headers are over :D
		while requestline != '\r\n':
			#here we first add the requestline instead of receiving to avoid adding the \r\n part
			headers += requestline
			requestline = self.rfile.readline()
		print requestline
		#remove the final \n and split the rest of the string to a list
		headers = headers.rstrip().split('\r\n')
		for header in headers:
			#we split the header in a key and a value (the value is split only 1 time because : might reoccur)
			key,value = header.split(':',1)
			values = value.split(',')
			if len(values) == 1:
				temp_dict[key] = value.strip()
			else:
				temp_dict[key] = values
		return temp_dict

	def send_headers(self,header,content):
		''' send a header'''
		self.wfile.write('{}: {}\r\n'.format(header,content))

	def end_headers(self):
		'''send the separator between the headers and the content'''
		self.wfile.write('\r\n')

	def send_error(self,code,short = None, longer = None):
		#try to find the error in the responses tuple and if
		#its not there make it lel
		title,msg = self.responses[code]
		#send the actual first line
		self.send_response(code)
		#send the type of content that you are going to send
		self.send_headers('Content-Type','text/html')
		#close the connection cause ERROR
		self.send_headers('Connection','close')
		self.end_headers()
		#send the prewritten HTML error message
		self.wfile.write(self.error_message.format(title=title,code = code, explanation = msg))

	def send_response(self,code):
		to_send = '{} {} {}\r\n'.format(self.http_version, code, self.responses[code][0])
		self.wfile.write(to_send)

	def get(self):
		if self.path == '/':
			response_html = open('templates/index.html','r').read()
			self.send_response(200)
			self.send_headers('Content-Type','text/html')
			self.send_headers('Content-Length','{}'.format(len(response_html)))
			self.send_headers('Connection','close')
			self.end_headers()
			self.wfile.write(response_html)
		elif self.path == '/templates/style.css':
			response_css = open(self.path[1:]).read()
			self.send_response(200)
			self.send_headers('Content-Type','text/css')
			self.send_headers('Content-Length','{}'.format(len(response_css)))
			self.send_headers('Connection','close')
			self.end_headers()
			self.wfile.write(response_css)
		else:
			self.send_error(404)

	def post(self):
		print self.path
		if self.path == '/':
			to_get = int(self.headers['Content-Length'])
			if to_get > 1024:
				self.send_error(404)
			else:
				data = self.rfile.read(to_get)
			arg, value = data.split('=',1)
			p = requests.get('http://api.openweathermap.org/data/2.5/weather?q={}'.format(value))
		else:
			self.send_error(404)



if __name__=='__main__':
	server = ThreadingTCPServer(('',9996),WeatherRequestHandler)
	server.serve_forever()
