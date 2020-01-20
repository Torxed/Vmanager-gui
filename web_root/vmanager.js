function machine_stop(target) {
	socket.send({
		'_module' : 'machine',
		'target' : target,
		'action' : 'stop'
	})
}

function machine_start(target) {
	socket.send({
		'_module' : 'machine',
		'target' : target,
		'action' : 'start'
	})
}

function view_machines(view_details=false) {
	socket.send({
		'_module' : 'machines',
		'machines' : {
			'details' : view_details
		}
	})	
}

function view_nics(view_details=false) {
	socket.send({
		'_module' : 'virtualnics',
		'virtualnics' : {
			'details' : view_details
		}
	})	
}

function view_machine(target) {
	socket.send({
		'_module' : 'machine',
		'target' : target
	})
}

function view_nic(target) {
	socket.send({
		'_module' : 'virtualnic',
		'target' : target
	})
}

function view_harddrive(target) {
	socket.send({
		'_module' : 'harddrive',
		'target' : target
	})
}

function view_cdrom(target) {
	socket.send({
		'_module' : 'cdrom',
		'target' : target
	})
}

function view_router(target) {
	socket.send({
		'_module' : 'router',
		'target' : target
	})
}

function view_switch(target) {
	socket.send({
		'_module' : 'switch',
		'target' : target
	})
}

function create_machine(name, nics, harddrives, cd) {
	socket.send({
		'_module' : 'machine',
		'new' : {
			'name' : name,
			'nics' : nics,
			'harddrives' : harddrives,
			'cd' : cd
		}
	})
}

function create_nic(name) {
	socket.send({
		'_module' : 'virtualnic',
		'new' : {
			'name' : name
		}
	})
}

function create_switch(name) {
	socket.send({
		'_module' : 'switch',
		'new' : {
			'name' : name
		}
	})
}

function create_router(name, trunk) {
	socket.send({
		'_module' : 'router',
		'new' : {
			'name' : name,
			'trunk' : trunk
		}
	})
}

function change_interface_state(target, state) {
	socket.send({
		'_module' : 'interface',
		'state' : state,
		'target' : target
	})
}