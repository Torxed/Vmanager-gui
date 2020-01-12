import json
from os.path import isdir, isfile

class parser():
	def process(self, path, client, data, headers, fileno, addr, *args, **kwargs):
		print('### Machine ###\n', data, client)
		
		if 'target' in data:
			return {
				'machine' : data['target'],
				'data' : {
					'nics' : {
						'p0' : {'ip' : None, 'state' : 'up', 'connected_to' : None}
					},
				'hdds' : {
					'test0.qcow2' : {'size' : 5, 'format' : 'qcow2', 'snapshots' : True}
				},
				'cds' : {
					'archlinux-2019.11.29-x86_64.iso' : {'path' : '/home/anton/archinstall_iso/out/archlinux-2019.11.29-x86_64.iso', 'readonly' : True}
				}}
			}
		elif 'new' in data:
			machine = vmanager.Machine(name=data['new']['name'], display=True, harddrives=data['new']['harddrives'], nics=data['new']['nics'], cd=data['new']['cd'])
			machine.start_vm()