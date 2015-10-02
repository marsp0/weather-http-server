from SocketServer import *
import email.header
from time import sleep

class WeatherRequestHandler(StreamRequestHandler):

	def handle(self):
		request = self.rfile.readline()
		self.headers = self.get_headers()
		for header,value in self.headers.items():
			print header+ ': ', value
		if request.startswith('GET'):
			self.wfile.write('HTTP/1.1 200 OK\r\n')
			self.wfile.write('\r\n')
			self.wfile.write('<html><title>dsa</title><body><p>teh feck _</p></body></html>')


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
				temp_dict[key] = value
			else:
				temp_dict[key] = values
		return temp_dict



if __name__=='__main__':
	server = ThreadingTCPServer(('',9998),WeatherRequestHandler)
	server.serve_forever()
