#import lzw # Was slightly broken spewing out "EOS" errors.
import pyglet, json
from pyglet.gl import *
from collections import OrderedDict
from os import urandom, walk
from os.path import isfile, abspath
from math import *
from time import time, sleep
from json import loads, dumps
from subprocess import Popen, PIPE, STDOUT
from hashlib import sha256
#from pytun import TunTapDevice, IFF_TAP
#from pyroute2 import IPDB, IPRoute, netns, NetNS
#from pprint import pprint

pyglet.options['audio'] = ('alsa', 'openal', 'silent')
key = pyglet.window.key

gl_meta = {
	'viewport' : {'x' : 0, 'y' : 0, 'dx' : 0, 'dy' : 0}
}

#from config import conf

__builtins__.__dict__['config'] = {
	'resolution' : {'scale' : 1.0, 'width' : 800, 'height' : 600},
	'quit' : False,
	'pages' : {'default' : {'batch' : pyglet.graphics.Batch(),
							'layers' : {0 : pyglet.graphics.OrderedGroup(0),
									    1 : pyglet.graphics.OrderedGroup(1),
										2 : pyglet.graphics.OrderedGroup(2),
										3 : pyglet.graphics.OrderedGroup(3)},
							'sprites' : OrderedDict(),
							'subpages' : {}}
			   },
	'active_page' : 'default',
	'linkage' : False,

	'virtual_machines' : {},
	'virtual_interfaces' : {},
	'virtual_namespaces' : {},

	'font' : {'size' : 10, 'family' : None}
}

def genUID():
	#return hash(bytes(str(time()), 'UTF-8')+urandom(4))
	return sha256(bytes(str(time), 'UTF-8')+urandom(4)).hexdigest()

def gen_solid_image(width, height, color='#FF0000', alpha=255):
		if type(color) == str:
			c = color.lstrip("#")
			c = max(6-len(c),0)*"0" + c
			r = int(c[:2], 16)
			g = int(c[2:4], 16)
			b = int(c[4:], 16)
		else:
			r,g,b = color
		
		c = (r,g,b,alpha)
		return pyglet.image.SolidColorImagePattern(c).create_image(width, height)

def flush_dialogues(*args, **kwargs):
	if 'settings' in config['pages'][config['active_page']]['sprites']:
		config['pages'][config['active_page']]['sprites']['settings']._delete()
		del(config['pages'][config['active_page']]['sprites']['settings'])

def comp_settings(x, y, **configuration):
	if 'settings' in config['pages'][config['active_page']]['sprites']:
		config['pages'][config['active_page']]['sprites']['settings']._delete()
		del(config['pages'][config['active_page']]['sprites']['settings'])

	print(config['virtual_machines'][configuration['id']])
	config['pages'][config['active_page']]['sprites']['settings'] = menu({'Start' : start_comp, 'Delete' : delete_comp}, x, y)

def copy_template(x, y, **configuration):
	_id_ = genUID()
	config['virtual_machines'][_id_] = configuration#config['virtual_machines'][configuration['id']]
	config['pages'][config['active_page']]['sprites'][_id_] = computer(texture=configuration['icon'], width=30, height=30, x=x-15, y=y-15, txtmode='under', rbind=comp_settings, rparams={'id' : _id_})

def add_computer(x, y, **configuration):
	_id_ = genUID()
	print(x, y)
	config['pages'][config['active_page']]['sprites'][_id_] = computer(x=x-15-gl_meta['viewport']['x'], y=y-15-gl_meta['viewport']['y'], name=_id_, txtmode='under', rbind=comp_settings, rparams={'id' : _id_})

#	with IPDB() as ip:
#		config['virtual_interfaces'][_id_] = ip.create(ifname='v0p0', kind='veth', peer='v0p1').commit()
#		config['virtual_namespaces'][_id_] = {'v0p0' : False, 'v0p1' : True}
#		config['pages'][config['active_page']]['sprites'][_id_].tap = 'v0p0'
#		
#		netns.create(_id_)
#		with ip.interfaces.v0p1 as veth:
#			veth.net_ns_fd = _id_

		#ns = NetNS(_id_)
		#pprint(ns)
		#ns.close()

def add_router(x, y):
	config['pages'][config['active_page']]['sprites']['router'+str(len(config['pages'][config['active_page']]['sprites']))] = router(x=x-15, y=y-15, txtmode='under')

def add_switch(x, y):
	_id_ = genUID()
	name = 'switch'+str(len(config['virtual_interfaces']))
	config['pages'][config['active_page']]['sprites'][_id_] = switch(x=x-15, y=y-15, txtmode='under', name=name)
	
#	with IPDB() as ip:
#		# Create the bridge:
#		with ip.create(kind='bridge', ifname=name) as i:
#			config['virtual_interfaces'][name] = {'ifi_type' : -1, 'ifname' : name}
#			print('Created switch')
#			#i.add_port('lo')
#			#i.add_ip('10.0.8.2/24')

	#config['virtual_interfaces'][name] = TunTapDevice(name=name, flags=IFF_TAP)
	#config['virtual_interfaces'][name].addr = '10.8.0.2'
	#config['virtual_interfaces'][name].dstaddr = '10.8.0.2'
	#config['virtual_interfaces'][name].netmask = '255.255.255.0'
	##config['virtual_interfaces'][name].mtu = 1500

	##config['virtual_interfaces'][name].persist(True)
	#config['virtual_interfaces'][name].up()

def start_comp(*args, **kwargs):
	pass

def delete_comp(*args, **kwargs):
	pass

class generic_sprite(pyglet.sprite.Sprite):
	def __init__(self, texture=None, width=None, height=None, color="#C2C2C2", alpha=int(0), x=None, y=None, moveable=False, clickable=True, batch=None, group=None, bind=None, label='', bparams={}, rparams={}, rbind=None, dbind=None, txtmode=None, name=None, linkable=False, *args, **kwargs):
		
		if not width:
			width = 10
			width_scale = width
			scale = None
		else:
			width_scale = float(width)
			scale = True
		if not height:
			height = 10
			height_scale = height
			scale = None
		else:
			height_scale = float(height)
			scale = True

		if type(texture) == str:
			if not texture or not isfile(abspath(texture)):
				#print('No texutre could be loaded for sprite, generating a blank one.')
				## If no texture was supplied, we will create one
				self.texture = gen_solid_image(int(width), int(height), color, alpha)
			else:
				self.texture = pyglet.image.load(abspath(texture))

		elif texture is None:
			self.texture = gen_solid_image(int(width), int(height), color, alpha)
		else:
			self.texture = texture

		if not batch:
			batch = config['pages'][config['active_page']]['batch']
		self._batch = batch

		if not group:
			group = 0
		if type(group) != int:
			raise ValueError('Group number needs to be of type INT in order to function.')
		self.group_nr = group
		group = config['pages'][config['active_page']]['layers'][group]
		
		tmp = super(generic_sprite, self).__init__(self.texture, batch=self._batch, group=group)
		#self.batch = batch
		#self.scale = config['resolution']['scale']
		if scale:
			self.scale = min(width_scale/self.image.width, height_scale/self.image.height)
		self.sprites = OrderedDict()

		if x:
			self.x = x
		else:
			self.x = 0
		if y:
			self.y = y
		else:
			self.y = 0

		if not name:
			name = genUID()
		self.name = name
		self.last_click = time()-60

		self.text = label
		self.txtmode = txtmode
		if not txtmode or txtmode == 'center':
			self.txtLabel = pyglet.text.Label(self.text, x=self.x+self.width/2, y=self.y+self.height/2, anchor_x='center', anchor_y='center', batch=self.batch, group=config['pages'][config['active_page']]['layers'][self.group_nr+1] if group else None)
		elif txtmode == 'under':
			self.txtLabel = pyglet.text.Label(self.text, x=self.x+self.width/2, y=self.y-12, anchor_x='center', anchor_y='center', batch=self.batch, group=config['pages'][config['active_page']]['layers'][self.group_nr+1] if group else None)
		else:
			self.txtLabel = pyglet.text.Label(self.text, x=self.x, y=self.y+self.height/2, anchor_x='left', anchor_y='center', batch=self.batch, group=config['pages'][config['active_page']]['layers'][self.group_nr+1] if group else None)

		self.moveable = moveable
		self.clickable = clickable
		self.linkable = linkable

		if bind:
			self.clickAction = bind
		else:
			self.clickAction = self.dummy
		self.bindParams = bparams

		if rbind:
			self.rClickAction = rbind
		else:
			self.rClickAction = self.dummy
		self.rClickParams = rparams

		if dbind:
			self.doubleClickAction = dbind
		else:
			self.doubleClickAction = self.dummy

		self.links = {}

	def set_batch(self, batch, group=None):
		self.batch = batch
		self.txtLabel.batch = batch
		if group:
			self.group = group
			self.txtLabel.group = group
		for sName, sObj in self.sprites.items():
			sObj.batch = batch
			if group:
				sObj.group = group

	def _delete(self):
		self.txtLabel.delete()
		for sprite in self.sprites:
			self.sprites[sprite]._delete()
		self.delete()

	def dummy(self, *args, **kwargs):
		pass

	def link(self, wif, recurse=True):
		## TODO: Give feedback to the "with" object if the link is possible
		if self.linkable:
			if recurse:
				if not wif.link(self, recurse=False):
					print('Target is not linkable.')
					return None

			if type(self) == computer and type(wif) == switch:
				print('Computer -> Switch')
#				with IPDB() as ip:
#					print('switch1.add_port(v0p0)')
#					ip.interfaces['switch1'].add_port('v0p0')

			#print('{}({}) -> {}({})'.format(self, type(self), wif, type(wif)))

			# config['pages'][config['active_page']]['batch']
			_id_ = ''.join(sorted([self.name, wif.name]))
			self.links[_id_] = (wif, line(self.batch, self.x+(self.width/2), self.y+(self.height/2), wif.x+(wif.width/2), wif.y+(wif.height/2), color=(255,0,0,255)))
			return True
		return False

	def click(self, x, y):
		"""
		Usually click_check() is called followed up
		with a call to this function.
		Basically what this is, is that a click
		should occur within the object.
		Normally a class who inherits Spr() will create
		their own click() function but if none exists
		a default must be present.
		"""
		if self.doubleClickAction and time()-self.last_click < 0.25:
			self.doubleClickAction(x, y)
		elif self.clickAction:
			self.clickAction(x, y, **self.bindParams)
		else:
			self.last_click = time()
			return True
		self.last_click = time()

	def rclick(self, x, y):
		if self.rClickAction:
			self.rClickAction(x, y, **self.rClickParams)

	def mouse_inside(self, x, y, button=None):
		"""
		When called, we first iterate our sprites.
		If none of those returned a click, we'll
		check if we're inside ourselves.
		This is because some internal sprites might go
		outside of the object boundaries.
		"""

		for sName, sObj in self.sprites.items():
			if sObj.clickable:
				check_sObj = sObj.mouse_inside(x, y, button)
				if check_sObj:
					return check_sObj

		if self.clickable:
			if x > self.x and x < (self.x + (self.texture.width*self.scale)):
				if y > self.y and y < (self.y + (self.texture.height*self.scale)):
					return self

	def move(self, x, y):
		if self.moveable:
			self.x += x
			self.y += y
			self.txtLabel.x += x
			self.txtLabel.y += y
			for sprite in self.sprites:
				self.sprites[sprite].move(x, y)#.x += x
				#self.sprites[sprite].y += y
				#self.sprites[sprite].txtLabel.x += x
				#self.sprites[sprite].txtLabel.y += y

			for index, (wif, line) in self.links.items():
				line.update_origin(self.x+(self.width/2), self.y+(self.height/2))
				wif.links[index][1].update_destination(self.x+(self.width/2), self.y+(self.height/2))

	def update(self):
		if len(self.text) and self.text != self.txtLabel.text:
			self.txtLabel.text = self.text

		if self.x != self.txtLabel.x or self.y != self.txtLabel.y:
			## TODO: Pretty massive CPU usage here, but meh w/e for now.
			if self.txtmode == 'center':
				self.txtLabel.x=self.x+self.width/2
				self.txtLabel.y=self.y+self.height/2
			#elif self.txtmode == 'left':
			#	self.txtLabel.x=self.x+self.width/2
			#	self.txtLabel.y=self.y+self.height/2
			elif self.txtmode == 'under':
				self.txtLabel.x=self.x+self.width/2
				self.txtLabel.y=self.y-12

	def add_subobj(self, obj, name=genUID(), *args, **kwargs):
		self.sprites[name] = obj(batch=self._batch, *args, **kwargs)

	def remove(self, obj_name):
		if obj_name in self.sprites:
			self.sprites[obj_name]._delete()

#	def click(self, x, y):
#		return True

	def _draw(self):
		self.draw()
		self.txtLabel.draw()

class computer(generic_sprite):
	def __init__(self, x=0, y=0, *args, **kwargs):
		if not 'moveable' in kwargs:
			kwargs['moveable'] = True
		if not 'txtmode' in kwargs:
			kwargs['txtmode'] = 'center'
		if not 'texture' in kwargs or kwargs['texture'] is None:
			kwargs['texture'] = gen_solid_image(30, 30, color='#00FF00')
		if not 'linkable' in kwargs:
			kwargs['linkable'] = True
		generic_sprite.__init__(self, group=2, x=x, y=y, dbind=self.doubleClick, rbind=self.rightClick, **kwargs)
		self.text = 'Computer'
		self.started = False
		self.tap = None

	def doubleClick(self, x, y):
		if not self.started:
			print('Booting up the PC')
			self.sprites['border'] = line(self.batch, self.x, self.y-3, self.x+self.width, self.y-3, color=(0,255,0,255))
			self.started = True
		else:
			print('Shutting it down')
			self.sprites['border'].delete()
			del(self.sprites['border'])
			self.started = False

	def start(self, *args, **kwargs):
		self.doubleClick(0,0)

	def stop(self, *args, **kwargs):
		self.doubleClick(0,0)

	def start_stop(self, *args, **kwargs):
		self.start() if not self.started else self.stop()
		self.remove('rmenu')

	def open_settings(self, *args, **kwargs):
		print('Opening settings dialoge for', self)
		self.remove('rmenu')

	def rightClick(self, x, y):
		menu_options = {
			'Start' if not self.started else 'Stop' : self.start_stop,
			'Settings' : self.open_settings
		}
		self.add_subobj(menu, 'rmenu', label='Menu: {}'.format(self), x=self.x, y=self.y, menu_options=menu_options)


class switch(generic_sprite):
	def __init__(self, x=0, y=0, **kwargs):
		if not 'moveable' in kwargs:
			kwargs['moveable'] = True
		if not 'txtmode' in kwargs:
			kwargs['txtmode'] = 'center'
		if not 'linkable' in kwargs:
			kwargs['linkable'] = True
		generic_sprite.__init__(self, group=1, texture=gen_solid_image(30, 30, color='#FF0000'), x=x, y=y, **kwargs)
		self.text = 'Switch'

class router(generic_sprite):
	def __init__(self, x=0, y=0, **kwargs):
		if not 'moveable' in kwargs:
			kwargs['moveable'] = True
		if not 'txtmode' in kwargs:
			kwargs['txtmode'] = 'center'
		if not 'linkable' in kwargs:
			kwargs['linkable'] = True
		generic_sprite.__init__(self, group=0, texture=gen_solid_image(30, 30, color='#0000FF'), x=x, y=y, **kwargs)
		self.text = 'Router'

class linker(generic_sprite):
	def __init__(self, x=0, y=0, **kwargs):
		if not 'moveable' in kwargs:
			kwargs['moveable'] = False

		self.on = gen_solid_image(30, 30, color='#55FF55')
		self.off = gen_solid_image(30, 30, color='#333333')
		generic_sprite.__init__(self, group=0, texture=self.off, x=x, y=y, txtmode='left', **kwargs)
		self.text = 'Link Mode'

	def click(self, x, y):
		if config['linkage']:
			self.texture = self.off
			self.image = self.texture
			config['linkage'] = False
		else:
			self.texture = self.on
			self.image = self.texture
			config['linkage'] = True
			
		if self.clickAction:
			self.clickAction(x, y)



class menu_entry(generic_sprite):
	def __init__(self, x=0, y=0, width=30, bind=None, **kwargs):
		if not 'moveable' in kwargs:
			kwargs['moveable'] = True

		self.backdrop = gen_solid_image(width, 30, color='#FF3333')
		generic_sprite.__init__(self, bind=bind, group=0, texture=self.backdrop, x=x, y=y+10, txtmode='left', clickable=True, **kwargs)

	def lClick(self, x, y, *args, **kwargs):
		print('Clicked menu at {}x{}'.format(x,y))

class menu(generic_sprite):
	def __init__(self, menu_options, x=0, y=0, **kwargs):
		if not 'moveable' in kwargs:
			kwargs['moveable'] = True

		self.backdrop = gen_solid_image((len(kwargs['label'])*config['font']['size']), 30, color='#FF3333')
		generic_sprite.__init__(self, bind=self.lClick, group=0, texture=self.backdrop, x=x+40, y=y+10, txtmode='center', clickable=True, **kwargs)

		y = self.y-30
		for label in menu_options:
			self.add_subobj(menu_entry, 'menu_entry_{}'.format(label), bind=menu_options[label], width=self.width, label=label, x=self.x, y=y)
			y -= 30

	def lClick(self, x, y, *args, **kwargs):
		print('Clicked menu at {}x{}'.format(x,y))

def dummy(*args, **kwargs):
	pass

class generic_shape():
	def __init__(self, batch, *args, **kwargs):
		#VertexList.__init__(self, *args, **kwargs)
		self.vertices = batch.add(*args, **kwargs)
		self.batch = batch
		group = args[2]
		if not group:
			group = 0
		if type(group) != int:
			raise ValueError('Group number needs to be of type INT (or None) in order to function.')
		self.group_nr = group
		self.clickable = False

	def dummy(self, *args, **kwargs):
		pass

	def click(self, x, y):
		pass

	def rclick(self, x, y):
		pass

	def mouse_inside(self, x, y, button=None):
		pass

	def move(self, x, y):
		pass

	def update(self):
		pass

	def delete(self):
		self.vertices.delete()

	def update_destination(self, x, y):
		pass

class line(generic_shape):
	def __init__(self, batch, sx, sy, ex, ey, color=(255,255,255,255), group=None):
		generic_shape.__init__(self, batch, 2, GL_LINES, group, ("v2f", (sx, sy, ex, ey)), ('c4B', color*2))
		self.x = sx
		self.y = sy
		self.width = max(sx, ex) - min(sx, ex)
		self.height = max(sy, ey) - min(sy, ey)
		self.text = ''
		self.txtLabel = pyglet.text.Label(self.text, x=self.x+self.width/2, y=self.y+self.height/2, anchor_x='center', anchor_y='center', batch=self.batch, group=config['pages'][config['active_page']]['layers'][self.group_nr+1] if group else None)

	def update_destination(self, x, y):
		#print(dir(self.vertices))
		self.vertices.vertices = self.vertices.vertices[0], self.vertices.vertices[1], x, y

	def update_origin(self, x, y):
		self.vertices.vertices = x, y, self.vertices.vertices[2], self.vertices.vertices[3]

class main(pyglet.window.Window):#								 config['resolution'].height()
	def __init__ (self, width=config['resolution']['width'], height=config['resolution']['height'], *args, **kwargs):
		super(main, self).__init__(width, height, *args, **kwargs)
		self.x, self.y = 0, 0

		self.active_sprites = OrderedDict()

		self.input = ''	
		self.keymap = {key._0 : 0, key._1 : 1, key._2 : 2, key._3 : 3, key._4 : 4, key._5 : 5, key._6 : 6, key._7 : 7, key._8 : 8, key._9 : 9}
		self.drag_origin = None

		self.keys = {}
		# DEBUG:
		self.combos = {}

		self.drag = False
		self.alive = 1
		glDepthFunc(GL_LEQUAL)
		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

		glViewport(0, 0, config['resolution']['width'], config['resolution']['height'])
		glOrtho(0, 2, 0, 2, -1, 1)
		#glFrustum(0,1, 0,1, 0,1)
		glMatrixMode(GL_MODELVIEW)

	def on_draw(self):
		self.render()

	def on_close(self):
		self.alive = 0

		# {'ad157386ce73779e38a9d092de23b947ba51561c9bfb2b294be3cea32e772f96': {'mtu': 1500, 'kind': 'veth', 'gso_max_segs': 65535, 'ifname': 'v0p0', 'ipdb_priority': 0, 'gso_max_size': 65536, 'operstate': 'DOWN', 'peer': 'v0p1', 'carrier': 0, 'num_tx_queues': 1, 'carrier_changes': 1, 'broadcast': 'ff:ff:ff:ff:ff:ff', 'txqlen': 1000, 'ifi_type': 1, 'group': 0, 'qdisc': 'noop', 'index': 37, 'link': 36, 'num_rx_queues': 1, 'family': 0, 'ipdb_scope': 'detached', 'ipaddr': (), 'ports': (), 'linkmode': 0, 'flags': 4098, 'proto_down': 0, 'promiscuity': 0, 'neighbours': (), 'address': '2e:22:86:34:6e:bd', 'vlans': ()}}
		# {'ad157386ce73779e38a9d092de23b947ba51561c9bfb2b294be3cea32e772f96': {'v0p0': False, 'v0p1': True}}
		
		with IPRoute() as ip:
			for interface in config['virtual_interfaces']:
				ip.link('delete', ifname=config['virtual_interfaces'][interface]['ifname'])
				#ip.link('delete', index=config['virtual_interfaces'][interface]['index'])

			for ns in config['virtual_namespaces']:
				#config['virtual_namespaces'][ns]
				netns.remove(ns)
				#config['virtual_interfaces'][switch].persist(False)
				#config['virtual_interfaces'][switch].down()
				#config['virtual_interfaces'][switch].close()

	def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
		self.drag = True

		if config['linkage']:
			if not len(self.active_sprites):
				return None
			else:
				if not self.drag_origin:
					sprName = list(self.active_sprites)[0]
					self.drag_origin = config['pages'][config['active_page']]['sprites'][sprName]
				else:
					if not 'connecting_line' in config['pages'][config['active_page']]['sprites']:
						config['pages'][config['active_page']]['sprites']['connecting_line'] = line(config['pages'][config['active_page']]['batch'], self.drag_origin.x+(self.drag_origin.width/2), self.drag_origin.y+(self.drag_origin.height/2), x, y)

					config['pages'][config['active_page']]['sprites']['connecting_line'].update_destination(x, y)

					#glColor4f(255, 255, 255, 255)
					#glBegin(GL_LINES)
					#glVertex2f(self.drag_origin[0], self.drag_origin[1])
					#glVertex2f(x, y)
					#glEnd()
	#				pyglet.graphics.draw(2, GL_LINES, ('v2i', (self.drag_origin[0], self.drag_origin[1], x, y)))
		else:
			if len(self.active_sprites):
				for name, obj in self.active_sprites.items():
					obj.move(dx, dy)
					if not key.LSHIFT in self.keys:
						break
			else:
				gl_meta['viewport']['x'] += dx
				gl_meta['viewport']['y'] += dy
				gl_meta['viewport']['dx'] += dx
				gl_meta['viewport']['dy'] += dy

				#glTranslatef(0, 0, 0.1)

	def on_key_release(self, symbol, modifiers):
		if symbol == key.LCTRL:
			self.active_sprites = OrderedDict()

		try:
			del self.keys[symbol]
		except:
			pass

	def on_mouse_release(self, x, y, button, modifiers):
		#if button == 1:
		if config['linkage'] and self.drag_origin:
			for sprite_name, sprite in config['pages'][config['active_page']]['sprites'].items():
				if sprite:
					sprite_obj = sprite.mouse_inside(x, y, button)
					if sprite_obj:
						#print('Linking',self.drag_origin,'with', sprite_obj)
						self.drag_origin.link(sprite_obj)

			if 'connecting_line' in config['pages'][config['active_page']]['sprites']:
				config['pages'][config['active_page']]['sprites']['connecting_line'].delete()
				del(config['pages'][config['active_page']]['sprites']['connecting_line'])
		else:
			for sName, sObj in self.active_sprites.items():
				if button == 1:
					sObj.click(x, y)
				else:
					sObj.rclick(x, y)

		if not key.LCTRL in self.keys:
			self.active_sprites = OrderedDict()

		self.drag_origin = None

	def on_mouse_press(self, x, y, button, modifiers):
		#if button == 1:
		for sprite_name, sprite in config['pages'][config['active_page']]['sprites'].items():
			if sprite:
				#print('Clickchecking:', sprite, 'with button', button)
				sprite_obj = sprite.mouse_inside(x, y, button)
				if sprite_obj:
					self.active_sprites[sprite_name] = sprite_obj
					#print('Activated {} (Ctrl: {})'.format(sprite_name, (key.LCTRL in self.keys)))
					if not key.LSHIFT in self.keys:
						break

		## TODO: This is a bit shaky, doesn't look clean enough.
		if not len(self.active_sprites):
			flush_dialogues()

	def on_key_press(self, symbol, modifiers):
		self.keys[symbol] = True

		if symbol == key.ESCAPE: # [ESC]
			self.alive = 0

		elif symbol in self.keymap:
			self.input += str(self.keymap[symbol])

		elif symbol == key.BACKSPACE:
			self.input = self.input[:-1]

		elif symbol == key.RIGHT:
			pass
			#for sName, sObj in config['pages'][config['active_page']]['sprites'].items():
			#	sObj.update()

		elif symbol == key.ENTER:
			self.input = ''
		#elif symbol == key.LCTRL:

	def render(self):
		self.clear()

		for sName, sObj in config['pages'][config['active_page']]['sprites'].items():
			sObj.update()

		#glViewport(gl_meta['viewport']['x'], gl_meta['viewport']['y'], config['resolution']['width']+gl_meta['viewport']['x'], config['resolution']['height']+gl_meta['viewport']['y'])
		config['pages'][config['active_page']]['batch'].draw()

		#glViewport(0, 0, config['resolution']['width'], config['resolution']['height'])
		config['pages'][config['active_page']]['menu'].draw()
		
		gl_meta['viewport']['dx'] = 0
		gl_meta['viewport']['dy'] = 0
		self.flip()

	def run(self):
		while self.alive == 1 and config['quit'] is False:
			self.render()

			# -----------> This is key <----------
			# This is what replaces pyglet.app.run()
			# but is required for the GUI to not freeze
			#
			event = self.dispatch_events()

		self.on_close()

config['pages'][config['active_page']]['menu'] = pyglet.graphics.Batch()
config['pages'][config['active_page']]['sprites']['btn_computer'] = computer(x=0, y=config['resolution']['height']-30, bind=add_computer, moveable=False, txtmode='left', batch=config['pages'][config['active_page']]['menu'])
config['pages'][config['active_page']]['sprites']['btn_router'] = router(x=0, y=config['resolution']['height']-60, bind=add_router, moveable=False, txtmode='left', batch=config['pages'][config['active_page']]['menu'])
config['pages'][config['active_page']]['sprites']['btn_switch'] = switch(x=0, y=config['resolution']['height']-90, bind=add_switch, moveable=False, txtmode='left', batch=config['pages'][config['active_page']]['menu'])
config['pages'][config['active_page']]['sprites']['linkButton'] = linker(x=0, y=config['resolution']['height']-120, moveable=False, batch=config['pages'][config['active_page']]['menu'])

struct = {
	'computers' : {
		'computer_1' : {'x' : 279, 'y' : 367, 'type' : 'computer'},
		'computer_2' : {'x' : 483, 'y' : 350, 'type' : 'computer'}
	},
	'switches' : {
		'switch_1' : {'x' : 370, 'y' : 215, 'type' : 'switch'}
	},
	'routers' : {},
	'links' : {
		'computer_1' : ['switch_1'],
		'computer_2' : ['switch_1']
	}
}

for uuid in struct['computers']:
	config['pages'][config['active_page']]['sprites'][uuid] = computer(**struct['computers'][uuid])

for uuid in struct['switches']:
	config['pages'][config['active_page']]['sprites'][uuid] = switch(**struct['switches'][uuid])

for link_src in struct['links']:
	if link_src in config['pages'][config['active_page']]['sprites']:
		for link_dst in struct['links'][link_src]:
			if link_dst in config['pages'][config['active_page']]['sprites']:
				print('Linking {} with {}'.format(link_src, link_dst))
				config['pages'][config['active_page']]['sprites'][link_src].link(config['pages'][config['active_page']]['sprites'][link_dst])
			else:
				print('Can not link {} with {}'.format(link_src, link_dst))
	else:
		print('Link source {} not in sprites.'.format(link_src))

#x = 31
#for root, folders, files in walk('./'):
#	for filename in files:
#		if not '.template' in filename:
#			continue
#
#		with open(filename) as template:
#			configuration = loads(template.read())
#
#		name = filename.rsplit('.',1)[0]
#		if not 'icon' in configuration or not isfile(abspath(configuration['icon'])):
#			if isfile(abspath('./icon_'+name+'.png')):
#				configuration['icon'] = abspath('./'+name+'.png')
#			else:
#				configuration['icon'] = None
#
#		config['pages'][config['active_page']]['sprites']['comp_'+name] = computer(texture=configuration['icon'], x=x, y=config['resolution']['height']-30, bind=copy_template, bparams=configuration, moveable=False, linkable=False, rbind=comp_settings, rparams={'name' : 'comp_'+name})
#		config['pages'][config['active_page']]['sprites']['comp_'+name].text = ''
#		config['pages'][config['active_page']]['sprites']['comp_'+name].scale = min(30.0/config['pages'][config['active_page']]['sprites']['comp_'+name].image.width, 30.0/config['pages'][config['active_page']]['sprites']['comp_'+name].image.height)
#		config['virtual_machines'][config['pages'][config['active_page']]['sprites']['comp_'+name].name] = configuration
#		x += 31

x = main()
x.run()