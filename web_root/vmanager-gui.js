let socket = null;

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
	if (typeof stats.id !== 'undefined')
		obj.id = stats.id;
	if (typeof stats.classList !== 'undefined')
		obj.classList = stats.classList;
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

function table(headers, entries, stats, parent, row_click=null) {
	let o = create_html_obj('table', stats, parent);

	let header = create_html_obj('tr', {'classList' : 'header'}, o);
	headers.forEach((title) => {
		let h = create_html_obj('td', {'classList' : 'header'}, header);
		h.innerHTML = title;
	})

	Object.keys(entries).forEach((row) => {
		let row_obj = create_html_obj('tr', {'classList' : 'row'}, o);
		let first_column = create_html_obj('td', {'classList' : 'column'}, row_obj);
		first_column.innerHTML = row;
		Object.keys(entries[row]).forEach((column) => {
			let column_obj = create_html_obj('td', {'classList' : 'column'}, row_obj);
			column_obj.innerHTML = entries[row][column];
		})

		if (row_click)
			row_obj.addEventListener('click', () => {
				row_click(row);
			});
	})

	return o;
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
			stop_machine.innerHTML = 'Stop machine';
			stop_machine.addEventListener('click', () => {
				socket.send({
					'_module' : 'machine',
					'target' : this.info['machine'],
					'action' : 'stop'
				})
			})
		} else {
			this.title = create_html_obj('h3', {'classList' : 'title machine_stopped'}, this.main_area);
			let start_machine = create_html_obj('button', {'classList' : 'button'}, this.submenu);
			start_machine.innerHTML = 'Start machine';
			start_machine.addEventListener('click', () => {
				socket.send({
					'_module' : 'machine',
					'target' : this.info['machine'],
					'action' : 'start'
				})
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
				socket.send({
					'_module' : 'virtualnic',
					'target' : row
				})
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
				socket.send({
					'_module' : 'harddrive',
					'target' : row
				})
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
				socket.send({
					'_module' : 'cdrom',
					'target' : row
				})
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

				this.machines = div({'classList' : 'machines'}, this.main_area);
				let machines_header = h3('Machines', {}, this.machines);
				let machine_list = table(
					['Machine Name', 'NIC\'s', 'Harddrives', 'CD\'s'],
					json_payload['machines'],
					{'classList' : 'table overview'}, this.machines, (row) => {
						socket.send({
							'_module' : 'machine',
							'target' : row
						})
				});

				console.log('Adding machines:', this.machines);
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
		add_machine.innerHTML = 'Add Machine';

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
					socket.send({
						'_module' : 'machine',
						'new' : {
							'name' : machine_name.value,
							'nics' : parseInt(machine_nics.value),
							'harddrives' : parseInt(machine_hdds.value),
							'cd' : machine_cd.value
						}
					})
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
						socket.send({
							'_module' : 'machine',
							'target' : row
						});
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