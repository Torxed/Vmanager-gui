import json
from os.path import isdir, isfile

class parser():
	def process(self, path, client, data, headers, fileno, addr, *args, **kwargs):
		print('### nic ###\n', data, client)
		
		if 'new' in data:
			vmanager.VirtualNic(data['new']['name'])