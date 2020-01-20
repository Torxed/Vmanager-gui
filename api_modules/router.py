import json
from os.path import isdir, isfile

def get_overview():
	response = {'vnics' : {}, 'interfaces' : {}, 'routers' : {}, 'switches' : {}}
	for nic_name in vmanager.nics:
		response['vnics'][nic_name] = {
			'ip' : vmanager.nics[nic_name].ip,
			'MAC' : vmanager.nics[nic_name].mac,
			'state' : vmanager.nics[nic_name].state,
			'gateway' : vmanager.nics[nic_name].ports['sink_name'],
			'routes' : None,
			'connected_to' : None
		}

	for nic_name in vmanager.interfaces:
		response['interfaces'][nic_name] = vmanager.interfaces[nic_name]

	for nic_name in vmanager.routers:
		response['routers'][nic_name] = vmanager.routers[nic_name]

	for nic_name in vmanager.switches:
		response['switches'][nic_name] = vmanager.switches[nic_name]

	return response

class parser():
	def process(self, path, client, data, headers, fileno, addr, *args, **kwargs):
		print('### router ###\n', data, client)
		
		if 'new' in data:
			vmanager.Router(trunk=data['new']['trunk'], ifname=data['new']['name'])

			return get_overview()