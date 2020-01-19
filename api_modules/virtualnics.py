import json
from os.path import isdir, isfile

def get_overview():
	response = {'nics' : {}}
	for nic_name in vmanager.nics:
		response['nics'][nic_name] = {
			'port' : vmanager.nics[nic_name].ports['source_name'],
			'sink' : vmanager.nics[nic_name].ports['sink_name']
		}

	for nic_name in vmanager.interfaces:
		response['nics'][nic_name] = vmanager.interfaces[nic_name]

	return response

def get_machine_info(target=None):
	pass

class parser():
	def process(self, path, client, data, headers, fileno, addr, *args, **kwargs):
		print('### NICS ###\n', data, client)
		
		if not 'target' in data:
			return get_overview()