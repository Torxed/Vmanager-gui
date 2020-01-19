import json
from os.path import isdir, isfile

def get_overview():
	response = {'nics' : {}}
	for nic_name in vmanager.nics:
		response['nics'][nic_name] = {
			'ip' : vmanager.nics[nic_name].ip,
			'MAC' : vmanager.nics[nic_name].mac,
			'state' : vmanager.nics[nic_name].state,
			'gateway' : vmanager.nics[nic_name].ports['sink_name'],
			'routes' : None,
			'connected_to' : None
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