import json
from os.path import isdir, isfile

def get_machine_status(machine_name):
	if not machine_name in vmanager.machines:
		return None, None
	
	machine = vmanager.machines[machine_name]

	nics = {}
	for nic in machine.nics:
		nics[str(nic)] = {'ip' : None, 'state' : nic.state, 'connected_to' : None}

	hdds = {}
	for hdd in machine.harddrives:
		hdds[hdd.filename] = {'size' : hdd.size, 'format' : hdd.format, 'snapshots' : False}

	cd = machine.cd.filename
	
	return machine, {
		'machine' : machine_name,
		'is_running' : machine.is_running(),
		'data' : {
			'nics' : nics,
			'hdds' : hdds,
			'cds' : cd
		}
	}

def notify_stop(client, machine_name):
	machine, machine_struct = get_machine_status(machine_name)
	client.send(bytes(json.dumps(machine_struct), 'UTF-8'))

class parser():
	def process(self, path, client, data, headers, fileno, addr, *args, **kwargs):
		print('### Machine ###\n', data, client)
		
		if 'target' in data:
			machine, machine_struct = get_machine_status(data['target'])

			if not machine_struct:
				return {
					'status' : 'failed',
					'message' : f'{data["target"]} does not exist.'
				}

			if 'action' in data:
				if data['action'] == 'start':
					machine.start_vm()
					machine_struct['is_running'] = True
				elif data['action'] == 'stop':
					machine.stop_vm(callback=notify_stop, client=client, machine_name=data['target'])
					machine_struct['is_running'] = False
			else:
				machine_struct['is_running'] = machine.is_running()

			return machine_struct
		elif 'new' in data:
			machine = vmanager.Machine(name=data['new']['name'], display=True, harddrives=data['new']['harddrives'], nics=data['new']['nics'], cd=data['new']['cd'])
			
			response = {'machines' : {}}
			for machine_name in vmanager.machines:
				response['machines'][machine_name] = {
					'nics' : len(vmanager.machines[machine_name].nics),
					'hdds' : len(vmanager.machines[machine_name].harddrives),
					'cds' : vmanager.machines[machine_name].cd.filename
				}

			return response