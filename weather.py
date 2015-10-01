from SocketServer import *
from socket import gethostname, getfqdn
import email.header
from time import sleep

class WeatherRequestHandler(StreamRequestHandler):

	def handle(self):
		requestline = ''
		request = ''
		while requestline != '\r\n':
			requestline = self.rfile.readline()
			request += requestline
		print request
		print 'shmuck'
		if request.startswith('GET'):
			self.wfile.write('HTTP/1.1 200 OK\r\n')
			self.wfile.write('\r\n')
			self.wfile.write('<html><title>dsa</title><body><p>teh feck _</p></body></html>')
			sleep(8)

if __name__=='__main__':
	server = ThreadingTCPServer(('',9997),WeatherRequestHandler)
	server.serve_forever()
