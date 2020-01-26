import json
from os.path import isdir, isfile

def get_overview():
	response = {'vnics' : {}, 'interfaces' : {}, 'routers' : {}, 'switches' : {}}
	for nic_name in vmanager.datastore['nics']:
		response['vnics'][nic_name] = {
			'ip' : vmanager.datastore['nics'][nic_name].ip,
			'MAC' : vmanager.datastore['nics'][nic_name].mac,
			'state' : vmanager.datastore['nics'][nic_name].state,
			'gateway' : vmanager.datastore['nics'][nic_name].gateway,
			'routes' : vmanager.datastore['nics'][nic_name].routes,
			'connected_to' : vmanager.datastore['nics'][nic_name].connected_to
		}

	for nic_name in vmanager.datastore['interfaces']:
		response['interfaces'][nic_name] = vmanager.datastore['interfaces'][nic_name]

	for nic_name in vmanager.datastore['routers']:
		response['routers'][nic_name] = vmanager.datastore['routers'][nic_name]

	for nic_name in vmanager.datastore['switches']:
		response['switches'][nic_name] = vmanager.datastore['switches'][nic_name]

	return response

class parser():
	def process(self, path, client, data, headers, fileno, addr, *args, **kwargs):
		if 'new' in data:
			vmanager.Router(trunk=data['new']['trunk'], ifname=data['new']['name'])

			return get_overview()