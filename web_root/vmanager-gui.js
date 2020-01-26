interfaces = {}

let elements = {}; // Used for popups
function popup(title_content, body_content, buttons_struct=null) {
	let div = document.createElement('div');
	let stylebar = document.createElement('div');
	stylebar.classList = 'stylebar';
	div.id = 'popup_'+(Math.random() * 1001);
	div.classList = 'popup';
	let title = document.createElement('div');
	title.classList = 'title';
	if(typeof title_content === 'string')
		title.innerHTML = title_content;
	else
		title.appendChild(title_content);
	let body = document.createElement('div');
	body.classList = 'body';
	if(typeof body_content === 'string')
		body.innerHTML = body_content;
	else
		body.appendChild(body_content);
	
	div.appendChild(stylebar);
	div.appendChild(title);
	div.appendChild(body);
	
	if(buttons_struct) {
		let buttons = document.createElement('div');
		buttons.classList = 'buttons';
		Object.keys(buttons_struct).forEach(function(label, index) {
			let button = document.createElement('button');
			button.innerHTML = label;
			button.classList = label;
			button.addEventListener('click', function(event) {
				buttons_struct[label](div);
			});
			buttons.appendChild(button);
		})
		div.appendChild(buttons);
	}
	elements[title] = div;
	document.getElementsByTagName("body")[0].appendChild(div);
	return div;
}

function append_stats_to_html_obj(obj, stats) {
	if (typeof stats === 'undefined')
		return;
	if (typeof stats.id !== 'undefined')
		obj.id = stats.id;
	if (typeof stats.classList !== 'undefined')
		obj.classList = stats.classList;
	if (typeof stats.innerHTML !== 'undefined')
		obj.innerHTML = stats['innerHTML'];
}

function create_html_obj(type, stats, parent) {
	let obj = document.createElement(type);
	append_stats_to_html_obj(obj, stats);

	if (parent)
		parent.appendChild(obj);

	return obj
}

function div(stats={}, parent=null) {
	return create_html_obj('div', stats, parent);
}

function h3(text, stats={}, parent=null) {
	let o = create_html_obj('h3', stats, parent);
	o.innerHTML = text;
	return o;
}

function table(headers, entries, stats, parent, row_click=null, special_columns={}) {
	let o = create_html_obj('table', stats, parent);

	let header = create_html_obj('tr', {'classList' : 'tableheader'}, o);
	headers.forEach((title) => {
		let h = create_html_obj('td', {'classList' : 'tableheader'}, header);
		h.innerHTML = title;
	})

	Object.keys(entries).forEach((row) => {
		let row_obj = create_html_obj('tr', {'classList' : 'row'}, o);
		let first_column = create_html_obj('td', {'classList' : 'column'}, row_obj);
		first_column.innerHTML = row;
		Object.keys(entries[row]).forEach((column) => {
			if (typeof special_columns[column] !== 'undefined') {
				let special_obj = special_columns[column](row, column, entries[row][column]);
				if(special_obj) {
					let column_obj = create_html_obj('td', {'classList' : 'column'}, row_obj);
					column_obj.appendChild(special_obj);
				}
			} else {
				let column_obj = create_html_obj('td', {'classList' : 'column'}, row_obj);
				column_obj.innerHTML = entries[row][column];
			}
		})

		if (row_click)
			row_obj.addEventListener('click', () => {
				row_click(row);
			});
	})

	return o;
}

function update_interface_cache(json) {
	Object.keys(json).forEach((category) => {
		interfaces[category] = json[category];
	})
}

function slider(row, column, data) {
	let _switch = create_html_obj('div', {'classList' : 'onoffswitch'})
	let input = create_html_obj('input', {'classList' : 'onoffswitch-checkbox', 'id' : 'slider_'+row}, _switch);
	input.type = 'checkbox';
	input.name = 'onoffswitch';
	if(data === true || data == 'up')
		input.checked = true;
	else
		input.checked = false;

	let label = create_html_obj('label', {'classList' : 'onoffswitch-label'}, _switch)
	label.htmlFor = 'slider_'+row;

	let spaninner = create_html_obj('span', {'classList' : 'onoffswitch-inner'}, label);
	let spanswitch = create_html_obj('span', {'classList' : 'onoffswitch-switch'}, label);

	return _switch
}

function connected_to(row, column, data) {
	let dropdown = document.createElement('select');
	dropdown.classList = 'dropdown';
	dropdown.id = row+'_connect_to';
	dropdown.setAttribute('nic', row);

	let none = document.createElement('option');
	none.classList = 'bold';
	none.innerHTML = 'No connection';
	dropdown.appendChild(none);

	Object.keys(interfaces).forEach((category) => {
		if (interfaces[category] && typeof interfaces[category] == 'object' && Object.keys(interfaces[category]).length) {
			let iface_category = document.createElement('option');
			iface_category.innerHTML = category + ':';
			iface_category.classList = 'bold';
			dropdown.appendChild(iface_category);
			Object.keys(interfaces[category]).forEach((iface_name) => {
				let option = document.createElement('option');
				option.value = iface_name;
				option.innerHTML = iface_name;
				dropdown.appendChild(option);
				if(data.indexOf(iface_name) >= 0)
					dropdown.value = iface_name;
			})
		}
	})

	dropdown.addEventListener('change', (event) => {
		socket.send({
			'_module' : 'interface',
			'target' : dropdown.getAttribute('nic'),
			'connect_to' : dropdown.options[dropdown.selectedIndex].value
		})
	})

	return dropdown;
}

class machine {
	constructor(info, container) {
		this.container = container;
		this.info = info;
		this.html_obj = this.build();

		console.log('Machine info:', info);
	}

	build() {
		this.container.innerHTML = '';
		console.log('Machine is rendering.')

		this.main_area = create_html_obj('div', {'classList' : 'machine'}, this.container);
		this.submenu = create_html_obj('div', {'classList' : 'submenu'}, this.main_area);


		if (this.info['is_running']) {
			this.title = create_html_obj('h3', {'classList' : 'title machine_started'}, this.main_area);
			let stop_machine = create_html_obj('button', {'classList' : 'button'}, this.submenu);
			let start_icon = create_html_obj('i', {'classList' : 'fas fa-power-off powerOff'}, stop_machine)
			stop_machine.innerHTML = stop_machine.innerHTML + ' Stop machine';
			stop_machine.addEventListener('click', () => {
				machine_stop(this.info['machine']);
			})
		} else {
			this.title = create_html_obj('h3', {'classList' : 'title machine_stopped'}, this.main_area);
			let start_machine = create_html_obj('button', {'classList' : 'button'}, this.submenu);
			let start_icon = create_html_obj('i', {'classList' : 'fas fa-power-off powerOn'}, start_machine)
			start_machine.innerHTML = start_machine.innerHTML + ' Start machine';
			start_machine.addEventListener('click', () => {
				machine_start(this.info['machine']);
			})
		}
		this.title.innerHTML = this.info['machine'];

		/*
			Render Network Interfaces:
		*/
		this.nics = div({'classList' : 'nics'}, this.main_area);
		this.nics_title = create_html_obj('h3', {'classList' : 'title'}, this.nics);
		this.nics_title.innerHTML = 'Network Interfaces:'
		let nic_list = table(
			['NIC Name', 'IP', 'State', 'Endpoint'],
			this.info['data']['nics'],
			{'classList' : 'table'}, this.nics, (row) => {
				view_nic(row);
		});

		/*
			Render Harddrives:
		*/
		this.hdds = div({'classList' : 'harddrives'}, this.main_area);
		this.hdds_title = create_html_obj('h3', {'classList' : 'title'}, this.hdds);
		this.hdds_title.innerHTML = 'Harddrives:'
		let hdd_list = table(
			['Harddrive', 'Size (GB)', 'Format', 'Snapshots'],
			this.info['data']['hdds'],
			{'classList' : 'table'}, this.hdds, (row) => {
				view_harddrive(row);
		});

		/*
			Render CD-rom's:
		*/
		this.cds = div({'classList' : 'cdroms'}, this.main_area);
		this.cds_title = create_html_obj('h3', {'classList' : 'title'}, this.cds);
		this.cds_title.innerHTML = 'CD-rom\'s:'
		let cd = this.info['data']['cds'];
		let cd_list = table(
			['CD-rom'],
			{[cd] : {}},
			{'classList' : 'table'}, this.cds, (row) => {
				view_cdrom(row);
		});
	}
}

class overview {
	constructor(container) {
		this.container = container;
		this.html_obj = this.build();
	}

	build() {
		this.container.innerHTML = '';
		
		console.log('Overview is rendering.')
		this.main_area = create_html_obj('div', {'classList' : 'overview'}, this.container);

		/*
			To be honest, create a machine-area in this.main_area
			and use the machines() class to render the machines.
			No point in duplicating code.. but works for now since
			there's more issues to tackle before this is useable.
		*/
		socket.subscribe('machines', (json_payload) => {
			console.log('Overview is rendering [data triggered].')
			if (typeof json_payload['machines'] !== 'undefined') {
				this.container.innerHTML = '';

				console.log(json_payload);

				this.machines = div({'classList' : 'machines'}, this.main_area);
				let machine_list = table(
					['Machine Name', 'NIC\'s', 'Harddrives', 'CD\'s'],
					json_payload['machines'],
					{'classList' : 'table overview'}, this.machines, (row) => {
						view_machine(row);
					},
					{
						'cds' : (row, column, data) => {
							let el = create_html_obj('div');
							el.innerHTML = data.split(/[\\\/]/).pop();
							return el;
						},
						'nics' : (row, column, data) => {
							console.log(row, column, data)
							let num = data.length;
							if(num > 2) {
								let obj = create_html_obj('span', {'classList' : 'nics'})
								obj.innerHTML = num;
								return obj
							} else {
								let container = create_html_obj('div', {'classList' : 'nics'});

								data.forEach((nic) => {
									let obj = create_html_obj('span', {'classList' : 'nic_item'}, container);
									obj.innerHTML = nic['ifname'] + ' (' + nic['mac'].toUpperCase() + ')';
								})

								return container
							}
						}
					});

				this.container.appendChild(this.machines);
			}
		})

		socket.subscribe('machine', (json_payload) => {
			console.log('Machine is rendering [data triggered].')
			let tmp = new machine(json_payload, document.querySelector('.body'));
		})

		return this.main_area.innerHTML;
	}
}

class machines {
	constructor(container) {
		this.container = container;
		this.html_obj = this.build();
	}

	build() {
		this.container.innerHTML = '';
		console.log('Machines is rendering.')
		socket.clear_subscribers();

		this.main_area = create_html_obj('div', {'classList' : 'overview'}, this.container);
		this.submenu = create_html_obj('div', {'classList' : 'submenu'}, this.main_area);
		let add_machine = create_html_obj('button', {'classList' : 'button'}, this.submenu);
		let plus_icon = create_html_obj('i', {'classList' : 'fas fa-plus-square'}, add_machine);
		add_machine.innerHTML = add_machine.innerHTML + ' Add Machine';

		add_machine.addEventListener('click', () => {
			let popup_body = document.createElement('div');
			popup_body.classList = 'card';

			let popup_header = document.createElement('div');
			popup_header.classList = 'popup_header';
			popup_header.innerHTML = 'Create a new Virtual Machine';
			popup_body.appendChild(popup_header);

			let machine_name = create_html_obj('input', {'classList' : 'popup_field'}, popup_body);
			machine_name.placeholder = 'Machine name';

			let machine_nics = create_html_obj('input', {'classList' : 'popup_field'}, popup_body);
			machine_nics.placeholder = 'Number of NIC\'s';

			let machine_hdds = create_html_obj('input', {'classList' : 'popup_field'}, popup_body);
			machine_hdds.placeholder = 'Number of Harddrives';

			let machine_cd = create_html_obj('input', {'classList' : 'popup_field'}, popup_body);
			machine_cd.placeholder = 'CD (iso) path';
			machine_cd.value = '/home/anton/archinstall_iso/out/archlinux-2019.11.29-x86_64.iso';

			popup("New Virtual Machine", popup_body, {
				"OK" : function(div) {
					create_machine(machine_name.value,
									parseInt(machine_nics.value),
									parseInt(machine_hdds.value),
									machine_cd.value)
					div.remove();
				},
				"Cancel" : function(div) {
					div.remove();
				}
			});
		})

		socket.subscribe('machines', (json_payload) => {
			console.log('Machines is rendering [data triggered].')
			if (typeof json_payload['machines'] !== 'undefined') {

				this.machines = div({'classList' : 'machines'}, this.main_area);
				let machines_header = h3('Machines', {}, this.machines);
				let machine_list = table(
					['Machine Name', 'NIC\'s', 'Harddrives', 'CD\'s'],
					json_payload['machines'],
					{'classList' : 'table machines'}, this.machines, (row) => {
						view_machine(row);
					},
					{
						'cds' : (row, column, data) => {
							let el = create_html_obj('div');
							el.innerHTML = data.split(/[\\\/]/).pop();
							return el;
						},
						'nics' : (row, column, data) => {
							console.log(row, column, data)
							let num = data.length;
							if(num > 2) {
								let obj = create_html_obj('span', {'classList' : 'nics'})
								obj.innerHTML = num;
								return obj
							} else {
								let container = create_html_obj('div', {'classList' : 'nics'});

								data.forEach((nic) => {
									let obj = create_html_obj('span', {'classList' : 'nic_item'}, container);
									obj.innerHTML = nic['ifname'] + ' (' + nic['mac'].toUpperCase() + ')';
								})

								return container
							}
						}
					})
				
				this.container.innerHTML = '';
				this.container.appendChild(this.main_area);
			}

		})

		socket.subscribe('machine', (json_payload) => {
			let tmp = new machine(json_payload, document.querySelector('.body'));
		})
		return this.main_area.innerHTML;
	}
}

class networkinterfaces {
	constructor(container) {
		this.container = container;
		this.html_obj = this.build();
	}

	build() {
		this.container.innerHTML = '';
		socket.clear_subscribers();
		this.main_area = create_html_obj('div', {'classList' : 'overview'}, this.container);
		this.submenu = create_html_obj('div', {'classList' : 'submenu'}, this.main_area);
		let add_interface = create_html_obj('div', {'classList' : 'button'}, this.submenu);
		let add_switch = create_html_obj('div', {'classList' : 'button'}, this.submenu);
		let add_router = create_html_obj('div', {'classList' : 'button'}, this.submenu);
		let refresh_interfaces = create_html_obj('div', {'classList' : 'button'}, this.submenu);
		let plus_icon = create_html_obj('i', {'classList' : 'fas fa-plus-square'}, add_interface);
		let refresh_icon = create_html_obj('i', {'classList' : 'fas fa-sync-alt'}, refresh_interfaces);
		plus_icon = create_html_obj('i', {'classList' : 'fas fa-plus-square'}, add_switch);
		plus_icon = create_html_obj('i', {'classList' : 'fas fa-plus-square'}, add_router);
		add_interface.innerHTML = add_interface.innerHTML + ' Add Virtual Interface';
		add_switch.innerHTML = add_switch.innerHTML + ' Add Virtual Switch';
		add_router.innerHTML = add_router.innerHTML + ' Add Virtual Router';
		refresh_interfaces.innerHTML = refresh_interfaces.innerHTML + ' Refresh interfaces';

		add_interface.addEventListener('click', () => {
			let popup_body = document.createElement('div');
			popup_body.classList = 'card';

			let popup_header = document.createElement('div');
			popup_header.classList = 'popup_header';
			popup_header.innerHTML = 'Create a new Virtual Network Interface';
			popup_body.appendChild(popup_header);

			let nic_name = create_html_obj('input', {'classList' : 'popup_field'}, popup_body);
			nic_name.placeholder = 'NIC Name';

			popup("New Virtual NIC", popup_body, {
				"OK" : function(div) {
					create_nic(nic_name.value);
					div.remove();
				},
				"Cancel" : function(div) {
					div.remove();
				}
			});
		})

		add_switch.addEventListener('click', () => {
			let popup_body = document.createElement('div');
			popup_body.classList = 'card';

			let popup_header = document.createElement('div');
			popup_header.classList = 'popup_header';
			popup_header.innerHTML = 'Create a new Virtual Switch';
			popup_body.appendChild(popup_header);

			let nic_name = create_html_obj('input', {'classList' : 'popup_field'}, popup_body);
			nic_name.placeholder = 'Switch Name';

			popup("New Virtual Switch", popup_body, {
				"OK" : function(div) {
					create_switch(nic_name.value);
					div.remove();
				},
				"Cancel" : function(div) {
					div.remove();
				}
			});
		})

		add_router.addEventListener('click', () => {
			let popup_body = document.createElement('div');
			popup_body.classList = 'card';

			let popup_header = document.createElement('div');
			popup_header.classList = 'popup_header';
			popup_header.innerHTML = 'Create a new Virtual Router';
			popup_body.appendChild(popup_header);

			let nic_name = create_html_obj('input', {'classList' : 'popup_field'}, popup_body);
			nic_name.placeholder = 'Router Name';

			let trunk = create_html_obj('input', {'classList' : 'popup_field'}, popup_body);
			trunk.placeholder = 'Trunk port (interface name)';
			trunk.value = 'ens4u1';

			popup("New Virtual Router", popup_body, {
				"OK" : function(div) {
					create_router(nic_name.value, trunk.value);
					div.remove();
				},
				"Cancel" : function(div) {
					div.remove();
				}
			});
		})

		refresh_interfaces.addEventListener('click', () => {
			socket.send({
				"_module": "virtualnics",
				"virtualnics": {
					"update" : true
				}
			})
		})

		socket.subscribe('vnics', (json_payload) => {
			console.log(json_payload)

			update_interface_cache(json_payload);

			if (typeof json_payload['vnics'] !== 'undefined') {
				this.main_area.innerHTML = '';
				this.main_area.appendChild(this.submenu)

				this.vnics = div({'classList' : 'vnics'}, this.main_area);
				let interfaces_header = h3('Physical Interfaces', {}, this.vnics);
				let interfaces_list = table(
					['NIC Name', 'IP(s)', 'MAC', 'State', 'Gateway', 'Routes', 'Connected to'],
					json_payload['interfaces'],
					{'classList' : 'table interfaces'}, this.vnics, (row) => {
						view_nic(row);
					},
					{
						'ifname' : () => {},
						'state' : (row, column, data) => {
							let obj = slider(row, column, data);
							obj.querySelector('input').setAttribute('nic', row);
							obj.addEventListener('click', (event) => {
								let slider_obj = event.target.parentElement.parentElement.querySelector('input');
								
								change_interface_state(slider_obj.getAttribute('nic'), slider_obj.checked);
							})
							return obj;
						}
					}
				)

				let vnics_header = h3('Virtual Interfaces', {}, this.vnics);
				let vnics_list = table(
					['NIC Name', 'IP(s)', 'MAC', 'State', 'Gateway', 'Routes', 'Connected to'], // Headers
					json_payload['vnics'], // Data to be parsed
					{'classList' : 'table vnics'}, // Set attributes on the table
					this.vnics, // Which parent are this table going to be inserted into
					(row) => { // What should happen when we click on each row?
						view_nic(row);
					},
					{ // Any special columns that we should render differently?
						'connected_to' : connected_to,
						'state' : (row, column, data) => {
							let obj = slider(row, column, data);
							obj.querySelector('input').setAttribute('nic', row);
							obj.addEventListener('click', (event) => {
								let slider_obj = event.target.parentElement.parentElement.querySelector('input');
								
								change_interface_state(slider_obj.getAttribute('nic'), slider_obj.checked);
							})
							return obj;
						}
					}
				)

				let switches_header = h3('Virtual Switches', {}, this.vnics);
				let switches_list = table(
					['NIC Name', 'IP(s)', 'MAC', 'State', 'Gateway', 'Routes', 'Trunk Connection'],
					json_payload['switches'],
					{'classList' : 'table switches'}, this.vnics, (row) => {
						view_switch(row);
					},
					{
						'ifname' : () => {},
						'connected_to' : connected_to,
						'state' : (row, column, data) => {
							let obj = slider(row, column, data);
							obj.querySelector('input').setAttribute('nic', row);
							obj.addEventListener('click', (event) => {
								let slider_obj = event.target.parentElement.parentElement.querySelector('input');
								
								change_interface_state(slider_obj.getAttribute('nic'), slider_obj.checked);
							})
							return obj;
						}
					}
				)

				let routers_header = h3('Virtual Routers', {}, this.vnics);
				let routers_list = table(
					['NIC Name', 'IP(s)', 'MAC', 'State', 'Gateway', 'Routes', 'Trunk Connection'],
					json_payload['routers'],
					{'classList' : 'table routers'}, this.vnics, (row) => {
						view_router(row);
					},
					{
						'ifname' : () => {},
						'trunk' : () => {}, // We'll use connected_to instead.
						'connected_to' : connected_to,
						'state' : (row, column, data) => {
							let obj = slider(row, column, data);
							obj.querySelector('input').setAttribute('nic', row);
							obj.addEventListener('click', (event) => {
								let slider_obj = event.target.parentElement.parentElement.querySelector('input');
								
								change_interface_state(slider_obj.getAttribute('nic'), slider_obj.checked);
							})
							return obj;
						}
					}
				)
				
				this.container.innerHTML = '';
				this.container.appendChild(this.main_area);
			}

		})

		socket.subscribe('nic', (json_payload) => {
			let tmp = new networkinterface(json_payload, document.querySelector('.body'));
		})
		return this.main_area.innerHTML;
	}
}