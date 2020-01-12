import json
from os.path import isdir, isfile

class parser():
	def process(self, path, client, data, headers, fileno, addr, *args, **kwargs):
		print('### Machines ###\n', data, client)
		
		if not 'machines' in data:
			response = {'machines' : {}}
			for machine_name in vmanager.machines:
				response['machines'][machine_name] = {
					'nics' : len(vmanager.machines[machine_name].nics),
					'hdds' : len(vmanager.machines[machine_name].harddrives),
					'cds' : vmanager.machines[machine_name].cd.filename
				}

			return response

		else:
			if 'details' in data['machines']:
				target = None
				if 'target' in data['machines']: target = data['machines']['target']

				response = {'machines' : {}}
				for machine_name in vmanager.machines:
					if target and machine_name != target: continue
					response['machines'][machine_name] = {
						'nics' : len(vmanager.machines[machine_name].nics),
						'hdds' : len(vmanager.machines[machine_name].harddrives),
						'cds' : vmanager.machines[machine_name].cd.filename
					}

				return response