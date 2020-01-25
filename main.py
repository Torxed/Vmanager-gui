import signal, time, json
import shlex, pty, os
import sys, traceback
import importlib.util
from os import walk, urandom, getcwd
from os.path import splitext, basename, isdir, isfile, abspath
from hashlib import sha512
from json import JSONEncoder, dumps, loads
from collections.abc import Iterator
from threading import Thread, enumerate as tenum
from select import epoll, EPOLLIN, EPOLLHUP
from subprocess import Popen, STDOUT, PIPE

def sig_handler(signal, frame):
	for handler in handlers:
		handler.close()
	exit(0)
signal.signal(signal.SIGINT, sig_handler)

## Set up logging early on:
import logging
from systemd.journal import JournalHandler

# Custom adapter to pre-pend the 'origin' key.
# TODO: Should probably use filters: https://docs.python.org/3/howto/logging-cookbook.html#using-filters-to-impart-contextual-information
class CustomAdapter(logging.LoggerAdapter):
	def process(self, msg, kwargs):
		return '[{}] {}'.format(self.extra['origin'], msg), kwargs

logger = logging.getLogger() # __name__
journald_handler = JournalHandler()
journald_handler.setFormatter(logging.Formatter('[{levelname}] {message}', style='{'))
logger.addHandler(journald_handler)
logger.setLevel(logging.DEBUG)

class LOG_LEVELS:
	CRITICAL = 1
	ERROR = 2
	WARNING = 3
	INFO = 4
	DEBUG = 5

def _log(*msg, origin='UNKNOWN', level=5, **kwargs):
	if level <= LOG_LEVEL:
		msg = [item.decode('UTF-8', errors='backslashreplace') if type(item) == bytes else item for item in msg]
		msg = [str(item) if type(item) != str else item for item in msg]
		log_adapter = CustomAdapter(logger, {'origin': origin})
		if level <= 1:
			log_adapter.critical(' '.join(msg))
		elif level <= 2:
			log_adapter.error(' '.join(msg))
		elif level <= 3:
			log_adapter.warning(' '.join(msg))
		elif level <= 4:
			log_adapter.info(' '.join(msg))
		else:
			log_adapter.debug(' '.join(msg))

class _safedict(dict):
	def __init__(self, *args, **kwargs):
		args = list(args)
		self.debug = False
		for index, obj in enumerate(args):
			if type(obj) == dict:
				m = safedict()
				for key, val in obj.items():
					if type(val) == dict:
						val = safedict(val)
					m[key] = val

				args[index] = m

		super(safedict, self).__init__(*args, **kwargs)

	def __getitem__(self, key):
		if not key in self:
			self[key] = safedict()

		val = dict.__getitem__(self, key)
		return val

	def __setitem__(self, key, val):
		if type(val) == dict:
			val = safedict(val)
		dict.__setitem__(self, key, val)

	def dump(self, *args, **kwargs):
		copy = safedict()
		for key in self.keys():
			val = self[key]
			if type(key) == bytes and b'*' in key: continue
			elif type(key) == str and '*' in key: continue
			elif type(val) == dict or type(val) == safedict:
				val = val.dump()
				copy[key] = val
			else:
				copy[key] = val
		return copy

	def copy(self, *args, **kwargs):
		return super(safedict, self).copy(*args, **kwargs)

def _importer(path):
	old_version = False
	log(f'Request to import "{path}"', level=6, origin='importer')
	if path not in modules:
		## https://justus.science/blog/2015/04/19/sys.modules-is-dangerous.html
		try:
			log(f'Loading API module: {path}', level=4, origin='importer')
			#importlib.machinery.SOURCE_SUFFIXES.append('') # empty string to allow any file
			spec = importlib.util.spec_from_file_location(path, path)
			modules[path] = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(modules[path])
			#sys.modules[path[:-3]] = modules[path]
			sys.modules[path] = modules[path]
			# if desired: importlib.machinery.SOURCE_SUFFIXES.pop()
			#modules[path] = importlib.import_module(path, path)
		except (SyntaxError, ModuleNotFoundError) as e:
			log(f'Failed to load API module ({e}): {path}', level=2, origin='importer')
			return None
	else:
		log(f'Reloading API module: {path}', level=4, origin='importer')
		#for key in sys.modules:
		#	print(key, '=', sys.modules[key])
		try:
			raise SyntaxError('https://github.com/Torxed/ADderall/issues/11')
			## Important: these two are crucial elements
			#importlib.invalidate_caches()

			#print('Reloading:', modules[path])
			#importlib.reload(modules[path])
		except SyntaxError as e:
			old_version = True
			log(f'Failed to reload API module ({e}): {path}', level=2, origin='importer')
	return old_version, modules[f'{path}']
__builtins__.__dict__['importer'] = _importer

def find_final_module_path(path, data):
	if '_module' in data:
		if data['_module'] in data and '_module' in data[data['_module']] and isdir(f"{path}/{data['_module']}"):
			return find_final_module_path(path=f"{path}/{data['_module']}", data=data[data['_module']])
		elif isfile(f"{path}/{data['_module']}.py"):
			return {'path' : f"{path}/{data['_module']}.py", 'data' : data, 'api_path' : ':'.join(f"{path}/{data['_module']}"[len('./api_modules/'):].split('/'))}

class pre_parser():
	def __init__(self, *args, **kwargs):
		self.parsers = safedict()

	def parse(self, client, data, headers, fileno, addr, *args, **kwargs):
		## This little bundle of joy, imports python-modules based on what module is requested from the client.
		## If the reload has already been loaded once before, we'll invalidate the python module cache and
		## reload the same module so that if the code has changed on disk, it will now be executed with the new code.
		##
		## This prevents us from having to restart the server every time a API endpoint has changed.

		# If the data isn't JSON (dict)
		# And the data doesn't contain _module, !abort!
		if not type(data) in (dict, safedict) or '_module' not in data:
			log(f'Invalid request sent, missing _module or _id in JSON data: {data[:200]}', level=3, origin='pre_parser', function='parse')
			return

		print(json.dumps(data, indent=4))

		## TODO: Add path security!
		module_to_load = find_final_module_path('./api_modules', data)
		if(module_to_load):
			import_result = importer(module_to_load['path'])
			if import_result:
				old_version, handle = import_result

				# Just keep track if we're executing the new code or the old, for logging purposes only
				if not old_version:
					log(f'Calling {handle}.parser.parse(client, data, headers, fileno, addr, *args, **kwargs)', level=4, origin='pre_parser', function='parse')
				else:
					log(f'Calling old {handle}.parser.parse(client, data, headers, fileno, addr, *args, **kwargs)', level=3, origin='pre_parser', function='parse')

				try:
					response = modules[module_to_load['path']].parser().process(f'api_modules', client, module_to_load['data'], headers, fileno, addr, *args, **kwargs)
					if response:
						if isinstance(response, Iterator):
							for item in response:
								yield {
									**item,
									'_id' : data['_id'] if '_id' in data else None,
									'_modules' : module_to_load['api_path']
								}
						else:
							yield {
								**response,
								'_id' : data['_id'] if '_id' in data else None,
								'_modules' : module_to_load['api_path']
							}
				except BaseException as e:
					log(f'Module error: {e}', level=2, origin='pre_parser', function='parse')
					traceback.print_exc()
		else:
			log(f'Invalid data, trying to load a inexisting module: {module_to_load} ({str(data)[:200]})', level=3, origin='pre_parser', function='parse')	

__builtins__.__dict__['LOG_LEVEL'] = LOG_LEVELS.INFO
__builtins__.__dict__['safedict'] = _safedict
__builtins__.__dict__['log'] = _log
__builtins__.__dict__['modules'] = safedict()
__builtins__.__dict__['importer'] = _importer
__builtins__.__dict__['sockets'] = safedict()
__builtins__.__dict__['config'] = safedict({
	'slimhttp': {
		'web_root': abspath('./web_root'),
		'index': 'index.html',
		'vhosts': {
			'vmanager.gui': {
				'web_root': abspath('./web_root'),
				'index': 'index.html'
			}
		}
	}
})

if isfile('datstore.json'):
	with open('datstore.json', 'r') as fh:
		log('Loading sample datastore from {{datstore.json}}', origin='STARTUP', level=5)
		__builtins__.__dict__['datastore'] = safedict(json.load(fh))

		#datastore = dict_to_safedict(datastore)
else:
	log(f'Starting with a clean database (reason: couldn\'t find {{datastore.json}})', origin='STARTUP', level=5)
	__builtins__.__dict__['datastore'] = safedict()


## Import sub-modules after configuration setup.
## (This so it doesn't break the logging..)
from dependencies.slimHTTP import slimhttpd
from dependencies.spiderWeb import spiderWeb
from dependencies.Vmanager import vmanager as _vmanager
from dependencies.olife import olife
__builtins__.__dict__['vmanager'] = _vmanager

with open('obtain.life.secrets', 'r') as fh:
	secrets = json.load(fh)
	
	__builtins__.__dict__['life'] = olife.obtain_life(secrets['shared'])
	life.subscribe('obtain.life', secrets['service_secret'])

websocket = spiderWeb.upgrader({'default': pre_parser()})
handlers = [
	slimhttpd.http_serve(upgrades={b'websocket': websocket}),
	slimhttpd.https_serve(upgrades={b'websocket': websocket}, cert='cert.pem', key='key.pem')
]

vmanager.get_memory_db()
vmanager.convert_memory_into_objects()
vmanager.update_interface_cache()
vmanager.save_db() # Start saving the database every 5 seconds

while 1:
	data = life.recv(timeout=0.025)
	life.parse(data)

	for handler in handlers:
		client = handler.accept()

		#for fileno, client in handler.sockets.items():
		for fileno, event in handler.poll().items():
			if fileno in handler.sockets:  # If not, it's a main-socket-accept and that will occur next loop
				sockets[fileno] = handler.sockets[fileno]
				client = handler.sockets[fileno]
				if client.recv():
					response = client.parse()
					if response:
						try:
							client.send(response)
						except BrokenPipeError:
							pass
						client.close()