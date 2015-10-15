import logging

class Logger(object):

	def __init__(self,name):

		logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(message)s', 
							filename='Logs/{name}.log'.format(name=name),
							level=logging.DEBUG)
		self.logger = logging.getLogger(name)
		self.name = name

	def info(self,data):
		self.logger.info(data)

	def warning(self,data):
		self.logger.warning(data)

	def debug(self,data):
		self.logger.debug(data)

	def get_name(self):
		return self.name

def arg_decorator(logger):

	def log_decorator(func):

		def wrapper(*args,**kwargs):

			logger.debug('Starting {}'.format(func.__name__))
			try:
				result = func(*args,**kwargs)
			except Exception as e:
				logger.warning('Error : '.format(e))
			else:
				logger.debug('Finished with success {}'.format(func.__name__))

if __name__ == '__main__':

	p = Logger('TrueTh')
	p.warning('dsadsa')