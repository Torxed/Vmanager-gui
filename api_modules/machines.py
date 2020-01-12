import json
from os.path import isdir, isfile

class parser():
	def process(self, path, client, data, headers, fileno, addr, *args, **kwargs):
		print('### Machines ###\n', data, client)
		
		if not 'machines' in data:
			response = {'machines' : {}}
			for machine_name in vmanager.machines:
				response['machines'][machine_name] = {
					'nics' : 0,
					'hdds' : 0,
					'cds' : 0
				}

			#return response
			return {'machines' : {'Machine0' : {'nics' : 2, 'hdds' : 1, 'cds' : 1}}}

		else:
			if 'details' in data['machines']:
				target = None
				if 'target' in data['machines']: target = data['machines']['target']

				response = {'machines' : {}}
				for machine_name in vmanager.machines:
					if target and machine_name != target: continue
					response['machines'][machine_name] = {
						'nics' : 0,
						'hdds' : 0,
						'cds' : 0
					}

				# return response
				return {'machines' : {'Machine0' : {'nics' : 2, 'hdds' : 1, 'cds' : 1}}}