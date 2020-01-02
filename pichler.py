import sys
import os
import nabto
import json
from collections import namedtuple
try:
	import configparser
except:
	# python2 compatibility
	import ConfigParser
	configparser = ConfigParser

package_dir = os.path.dirname(os.path.abspath(__file__))

class Pichler:
	# datapoint definitions
	DPItem = namedtuple('DPItem', ['addr', 'scale'])
	DP = {
		'StatusBits': DPItem((152, 1), 1),
		'Malfunction': DPItem((34, 0), 1),
		'CO2': DPItem((153, 1), 1),
		'Humidity': DPItem((154, 1), 1),
		'SCOP': DPItem((44, 0), 0.01),
		'HP.COP': DPItem((45, 0), 0.01),
		'HP.HeatingPower': DPItem((37, 0), 1),

		'Energy.Total': DPItem((65, 0), 1),
		'Energy.Heating': DPItem((64, 0), 1),
		'Energy.Cooling': DPItem((27, 0), 1),
		'Energy.HotWater': DPItem((38, 0), 1),
		'Energy.Ventilation': DPItem((29, 0), 1),

		'Power.HeatPump': DPItem((25, 0), 0.1),
		'Power.HotWater': DPItem((24, 0), 0.1),
		'Power.Ventilation': DPItem((26, 0), 0.1),

		'Temperature.Room': DPItem((19, 0), 0.01),

		'Temperature.Air.Supply': DPItem((1, 1), 0.01),
		'Temperature.Air.Extract': DPItem((6, 1), 0.01),
		'Temperature.Air.Outdoor': DPItem((2, 1), 0.01),
		'Temperature.Air.Exhaust': DPItem((3, 1), 0.01),

		'Temperature.Water.Center': DPItem((12, 1), 0.01),
		'Temperature.Water.Bottom': DPItem((13, 1), 0.01),

		'Ventilation.Level': DPItem((41, 1), 1),
		'Ventilation.Supply': DPItem((22, 0), 0.1),
		'Ventilation.Extract': DPItem((23, 0), 0.1),
	}

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

	# Get value of single datapoint
	# dp: datapoint name (see `DP` dict)
	# output: real value of given datapoint (scaled appropriately)
	def GetDatapoint(self, dp):
		item = self.DP[dp]
		return self.DatapointRawReadValue(item.addr[0], item.addr[1]) * item.scale

	# Get values of multiple datapoints
	# dps: list of datapoint names (see `DP` dict)
	# output: list of real values of given datapoints (same order as input list)
	def GetDatapoints(self, dps):
		l = []
		for dp in dps:
			item = self.DP[dp]
			l.append([item.addr[0], item.addr[1]])
		r = self.DatapointRawReadListValues(l)
		for i in range(len(dps)):
			item = self.DP[dps[i]]
			r[i] = r[i] * item.scale
		return r

	def RpcInvoke(self, command, params):
		r = self.session.RpcInvoke('nabto://%s/%s.json?%s' % (self.device, command, params))
		if r:
			return r['response']
		return []

	def Ping(self):
		return self.RpcInvoke('ping', 'ping=1885957735')

	def DatapointRawReadValues(self, address, obj, length):
		response = self.RpcInvoke('datapointReadValue', 'address=%d&obj=%d&length=%d' % (address, obj, length))
		if response:
			return [i['value'] for i in response['data']]
		return []

	def DatapointRawReadValue(self, address, obj=0):
		return self.DatapointRawReadValues(address, obj, 1)[0]

	# input : list of [addr, obj] pairs
	# output: list of raw values for each pair in original order
	def DatapointRawReadListValues(self, lst):
		l = [{'address': i[0], 'obj': i[1]} for i in lst]
		request = {'request': {'list': l}}
		response = self.RpcInvoke('datapointReadListValue', 'json=%s' % json.dumps(request))
		if response:
			return [i['value'] for i in response['data']]
		return []

	def SetpointRawReadValues(self, address, obj, length):
		response = self.RpcInvoke('setpointReadValue', 'address=%d&obj=%d&length=%d' % (address, obj, length))
		if response:
			return [i['value'] for i in response['data']]
		return []

	def SetpointRawReadValue(self, address, obj=0):
		return self.SetpointRawReadValues(address, obj, 1)[0]

	# input : list of [addr, obj] pairs
	# output: list of raw values for each pair in original order
	def SetpointRawReadListValues(self, lst):
		l = [{'address': i[0], 'obj': i[1]} for i in lst]
		request = {'request': {'list': l}}
		response = self.RpcInvoke('setpointReadListValue', 'json=%s' % json.dumps(request))
		if response:
			return [i['value'] for i in response['data']]
		return []
