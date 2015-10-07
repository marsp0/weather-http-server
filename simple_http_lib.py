#My effort of trying to build a simple httplib module
#just for the fun of it :)
#it works only for http

#my idea of how this should work 
#1. create and connect AF_INET, SOCK_STREAM socket
#2. connect to teh given address
#3. send the initial request
#4. get a response and parse it
#5. repeat i guess

import socket

'''Exceptions here'''

class BaseConnectionException(Exception):

	pass

class NotSupportedSchema(BaseConnectionException):

	def __init__(self, schema):
		self.schema = schema
		self.message = 'Schema missing or not supported'

class AddressException(BaseConnectionException):

	def __init__(self,address):
		self.address = address
		self.message = 'Wrong address'

class HeaderException(BaseConnectionException):

	def __init__(self,header):

		self.header = header

class AddHeaderError(HeaderException):

	def __init__(self,header):
		HeaderException.__init__(self,header)
		self.message = 'The argument must be tuple containing the header name and value in that order'

class HeaderDoesntExist(HeaderException):

	def __init__(self,header):
		HeaderException.__init__(self,header)
		self.message = 'The given header doesn\'t exist'

class Connection(object):

	def __init__(self, website):

		try:
			#the data passed after the address
			self.data = ''
			#the address of the host
			self.end_host = self.parse_link(website)
			#the HTTP port
			self.end_port = 80
			#generic headers that every request has
			self.headers = { 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
							'Host' : self.end_host,	
							'Accept-Encoding' : 'gzip, deflate, sdch',
							'Accept-Language' : 'en-US',
							'Connection' : 'keep-alive',
							'User-Agent' : 'Python-simple_http_lib-2.7',
							}
			#creating the socket and connecting instead of doing it manually
			self.sock = socket.create_connection((self.end_host,self.end_port))
			self.sock = self.sock.makefile()
			self.protocol_version = 'HTTP/1.1'
		#raise this error if the address is not starting with http or if its some other schema
		#for now we handle only http
		except NotSupportedSchema:
			raise
		#raising AddressException if for some reason the we can't connect
		#usually because of wrong address
		#no need to  raise the super generic socket.error
		except socket.error:
			raise AddressException(self.end_host)

	def parse_link(self,website):
		''' function to parse the website address'''
		#if it doesnt start with http:// it can be https which we dont support
		if website.startswith('http://'):
			temp_address = website[website.find('//')+2:]
			if '/' in temp_address:
				end_host, data = temp_address.split('/',1)
				if data != '':
					self.data = data
				return end_host
			else:
				return temp_address
		else:
			raise NotSupportedSchema(None)

	def get_headers(self):
		''' return headers dict'''
		return self.headers

	def string_headers(self):
		''' string representation of all the headers and the trailing line'''
		headers = ''.join(['{}: {}\r\n'.format(key,value) for key,value in self.headers.items()])
		#add the trailing line and return
		return headers + '\r\n'

	def add_header(self,hdr_tupl):
		''' try the add header'''
		try:
			self.headers[hdr_tupl[0]] = hdr_tupl[1]
		except IndexError:
			raise AddHeaderError(hdr_tupl)

	def modify_header(self,header,value):
		try:
			self.headers[header] = value
		except KeyError:
			raise HeaderDoesntExist(header)

	def delete_header(self,header):
		try:
			del self.headers[header]
		except KeyError:
			raise HeaderDoesntExist(header)

	def get(self):
		request_line = 'GET {} {}\r\n'
		if self.data:
			request_line = request_line.format('/'+self.data, self.protocol_version)
		elif self.data == '':	
			request_line = request_line.format('/',self.protocol_version)
		to_send = request_line + self.string_headers()
		self.sock.write(to_send)
		self.sock.flush()
		print repr(self.sock.readline())

class Response(object):

	def __init__(self,raw_response):
		pass

if __name__=='__main__':
	p = Connection('http://api.openweathermap.org/data/2.5/weather?q=London')
	p.get()