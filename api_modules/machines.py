import json
from os.path import isdir, isfile

def get_overview():
	response = {'machines' : {}}
	for machine_name in vmanager.machines:
		response['machines'][machine_name] = {
			'nics' : len(vmanager.machines[machine_name].nics),
			'hdds' : len(vmanager.machines[machine_name].harddrives),
			'cds' : vmanager.machines[machine_name].cd.filename
		}

	return response

def get_machine_info(target=None):
	response = {'machines' : {}}
	for machine_name in vmanager.machines:
		if target and machine_name != target: continue
		response['machines'][machine_name] = {
			'nics' : len(vmanager.machines[machine_name].nics),
			'hdds' : len(vmanager.machines[machine_name].harddrives),
			'cds' : vmanager.machines[machine_name].cd.filename
		}

	return response

class parser():
	def process(self, path, client, data, headers, fileno, addr, *args, **kwargs):
		if not 'machines' in data:
			return get_overview()

		else:
			if 'details' in data['machines'] and data['machines']['details']:
				target = None
				if 'target' in data['machines']: target = data['machines']['target']

				return get_machine_info(target)
			else:
				return get_overview()