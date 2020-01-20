import json
from os.path import isdir, isfile

class parser():
	def process(self, path, client, data, headers, fileno, addr, *args, **kwargs):
		print('### router ###\n', data, client)
		
		if 'new' in data:
			vmanager.Router(trunk=data['new']['trunk'], ifname=data['new']['name'])