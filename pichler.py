import sys
import os
import nabto
import json
try:
	import configparser
except:
	# python2 compatibility
	import ConfigParser
	configparser = ConfigParser

package_dir = os.path.dirname(os.path.abspath(__file__))

class Pichler:

	def __init__(self, device=None, user=None, passwd=None):
		if not device or not user or not passwd:
			config = configparser.ConfigParser()
			config.read(os.path.join(package_dir, 'pichler.ini'))

			if not device:
				device = config.get('pichler', 'device')
			if not user:
				user = config.get('pichler', 'user')
			if not passwd:
				passwd = config.get('pichler', 'pass')

		if not '.' in device:
			device += '.remote.lscontrol.dk'

		self.device = device
		self.client = nabto.Client(os.path.join(package_dir, '.home'))
		self.session = self.client.OpenSession(user, passwd)

		with open(os.path.join(package_dir, 'unabto_queries.xml'), 'r') as file:
		    rpc_xml = file.read()

		self.session.RpcSetDefaultInterface(rpc_xml)

	def RpcInvoke(self, command, params):
		r = self.session.RpcInvoke('nabto://%s/%s.json?%s' % (self.device, command, params))
		if r:
			return r['response']
		return []

	def Ping(self):
		return self.RpcInvoke('ping', 'ping=1885957735')

	def DatapointReadValues(self, address, obj, length):
		response = self.RpcInvoke('datapointReadValue', 'address=%d&obj=%d&length=%d' % (address, obj, length))
		if response:
			return [i['value'] for i in response['data']]
		return []

	def DatapointReadValue(self, address, obj=0):
		return self.DatapointReadValues(address, obj, 1)[0]

	# input : list of [addr, obj] pairs
	# output: list of values for each pair in original order
	def DatapointReadListValues(self, lst):
		l = [{'address': i[0], 'obj': i[1]} for i in lst]
		request = {'request': {'list': l}}
		response = self.RpcInvoke('datapointReadListValue', 'json=%s' % json.dumps(request))
		if response:
			return [i['value'] for i in response['data']]
		return []

	def SetpointReadValues(self, address, obj, length):
		response = self.RpcInvoke('setpointReadValue', 'address=%d&obj=%d&length=%d' % (address, obj, length))
		if response:
			return [i['value'] for i in response['data']]
		return []

	def SetpointReadValue(self, address, obj=0):
		return self.SetpointReadValues(address, obj, 1)[0]

	# input : list of [addr, obj] pairs
	# output: list of values for each pair in original order
	def SetpointReadListValues(self, lst):
		l = [{'address': i[0], 'obj': i[1]} for i in lst]
		request = {'request': {'list': l}}
		response = self.RpcInvoke('setpointReadListValue', 'json=%s' % json.dumps(request))
		if response:
			return [i['value'] for i in response['data']]
		return []
