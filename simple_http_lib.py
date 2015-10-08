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
from utils import responses
import json

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

'''Connection class for establishement of the connection '''

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

	def get(self,data = None):
		#prepare the request line with placeholders for the data path and the http version
		request_line = 'GET {} {}\r\n'
		if not data:
			#if the get method was called without any data, then we use the one passed to the constructor
			if self.data:
				request_line = request_line.format('/'+self.data, self.protocol_version)
			#if no data was passed to the constructor we just request the home page
			elif self.data == '':	
				request_line = request_line.format('/',self.protocol_version)
		else:
			#here we prepend the '/' to the path
			if not data.startswith('/'):
				request_line = request_line.format('/' + data, self.protocol_version)
			else:
				request_line = request_line.format(data, self.protocol_version)
		#prepare the whole request
		to_send = request_line + self.string_headers()
		#we send the info
		self.sock.write(to_send)
		#for some reason we have to flush manually because it stays in the buffer
		#i say for some reason because when i send info from the server to the client i dont have to call flush manually
		#probably there is some logic that i dont understand
		self.sock.flush()
		return self.handle_response()

	def handle_response(self):
		''' function that returns a response object '''
		#check the first line
		response = self.sock.readline().rstrip('\r\n')
		response_list = response.split()
		#split the response line and check the len
		if len(response_list) > 3:
			protocol = response_list[0]
			response_code = response_list[1]
			response_message = ' '.join(response_list[2:])
		else:
			protocol, response_code, response_message = response_list
		#start getting the headers
		response_line = ''
		response_header_string = ''
		while response_line != '\r\n':
			response_header_string += response_line
			response_line = self.sock.readline()
		#create a list from the header string
		response_headers = response_header_string.rstrip('\r\n').split('\r\n')
		#return the response if  there was no body to read
		if response_code.startswith('1') or response_code in ('204','304'):
			return Response((protocol, response_code, response_message), response_headers, responses[int(response_code)])
		else:
			#if there is body we ceck the Content length or the Transfer Encoding for the length of the body
			for header in response_headers:
				data = ''
				#check if the header is content length and get the body
				if header.startswith('Content-Length'):
					length = int(header[header.find(':')+1:].strip())
					data = self.sock.read(length)
					return Response((protocol, response_code, response_message), response_headers, data)
				#if on the other hand is Transfer-Envoding we again get the rest of the body
				elif header == 'Transfer-Encoding: chunked':
					while True:
						chunk_size = self.sock.readline()
						if chunk_size != '0\r\n':
							chunk_size = int('0x' + chunk_size.rstrip('\r\n'), 0)
							data = self.sock.read(chunk_size).rstrip('\n')
							_ = self.sock.readline()
						else:
							break
					return Response((protocol, response_code, response_message), response_headers, data)


class Response(object):

	def __init__(self,response_line_tuple, response_headers, response_body = None):
		self.response = response_line_tuple[1]
		self.protocol = response_line_tuple[0]
		self.response_short = response_line_tuple[2]
		self.headers = self.parse_headers(response_headers)
		self.text = response_body

	def parse_headers(self,headers_list):
		temp_dict = {}
		for header in headers_list:
			key,value = header.split(':',1)
			temp_dict[key] = value
		return temp_dict

	def jsonify(self):
		try:
			return json.loads(self.text)
		except ValueError:
			return self.text

if __name__=='__main__':
	p = Connection('http://api.openweathermap.org/data/2.5/weather?q=London')
	x = p.get()
	print x.jsonify()

