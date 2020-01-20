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
		print('### nic ###\n', data, client)
		
		if 'state' in data and 'target' in data:
			if data['target'] in vmanager.nics:
				if data['state']:
					vmanager.nics[data['target']].up()
				else:
					vmanager.nics[data['target']].down()
			elif data['target'] in vmanager.interfaces:
				if data['state']:
					vmanager.interfaces[data['target']].up()
				else:
					vmanager.interfaces[data['target']].down()
			elif data['target'] in vmanager.routers:
				if data['state']:
					vmanager.routers[data['target']].up()
				else:
					vmanager.routers[data['target']].down()
			elif data['target'] in vmanager.switches:
				if data['state']:
					vmanager.switches[data['target']].up()
				else:
					vmanager.switches[data['target']].down()
			else:
				print(f'[N] Could not locate {data["target"]}')

			return get_overview()