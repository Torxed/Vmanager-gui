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
		if 'state' in data and 'target' in data:
			if data['target'] in vmanager.datastore['nics']:
				if data['state']:
					vmanager.datastore['nics'][data['target']].up()
				else:
					vmanager.datastore['nics'][data['target']].down()
			elif data['target'] in vmanager.datastore['interfaces']:
				if data['state']:
					vmanager.datastore['interfaces'][data['target']].up()
				else:
					vmanager.datastore['interfaces'][data['target']].down()
			elif data['target'] in vmanager.datastore['routers']:
				if data['state']:
					vmanager.datastore['routers'][data['target']].up()
				else:
					vmanager.datastore['routers'][data['target']].down()
			elif data['target'] in vmanager.datastore['switches']:
				if data['state']:
					vmanager.datastore['switches'][data['target']].up()
				else:
					vmanager.datastore['switches'][data['target']].down()
			else:
				print(f'[N] Could not locate {data["target"]}')

			return get_overview()

		if 'connect_to' in data and 'target' in data:
			if data['target'] in vmanager.datastore['nics']:
				vmanager.datastore['nics'][data['target']].connect(data['connect_to'])
			elif data['target'] in vmanager.datastore['interfaces']:
				vmanager.datastore['interfaces'][data['target']].connect(data['connect_to'])
			elif data['target'] in vmanager.datastore['routers']:
				vmanager.datastore['routers'][data['target']].connect(data['connect_to'])
			elif data['target'] in vmanager.datastore['switches']:
				vmanager.datastore['switches'][data['target']].connect(data['connect_to'])
			return get_overview()