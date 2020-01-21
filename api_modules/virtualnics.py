import json
from os.path import isdir, isfile

def get_overview():
	response = {'vnics' : {}, 'interfaces' : {}, 'routers' : {}, 'switches' : {}}
	for nic_name in vmanager.nics:
		response['vnics'][nic_name] = {
			'ip' : vmanager.nics[nic_name].ip,
			'MAC' : vmanager.nics[nic_name].mac,
			'state' : vmanager.nics[nic_name].state,
			'gateway' : vmanager.nics[nic_name].gateway,
			'routes' : vmanager.nics[nic_name].routes,
			'connected_to' : vmanager.nics[nic_name].connected_to
		}

	for nic_name in vmanager.interfaces:
		response['interfaces'][nic_name] = vmanager.interfaces[nic_name]

	for nic_name in vmanager.routers:
		response['routers'][nic_name] = vmanager.routers[nic_name]

	for nic_name in vmanager.switches:
		response['switches'][nic_name] = vmanager.switches[nic_name]

	return response

def get_machine_info(target=None):
	pass

class parser():
	def process(self, path, client, data, headers, fileno, addr, *args, **kwargs):
		if 'virtualnics' in data and ('refresh' in data['virtualnics'] or 'update' in data['virtualnics']):
			vmanager.update_interface_cache()
		
		if not 'target' in data:
			return get_overview()