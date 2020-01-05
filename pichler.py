"""
Module for accessing Pichler heat pump unit
"""

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

class Pichler:
	"""
	A class for accessing Pichler heat pump unit.
	
	It allows to read runtime parameters (datapoints) as well as to read/write unit's settings (setpoints).
	
	Methods
	-------
	GetDatapoint(dp)
		Get value of single datapoint

	GetDatapoints(dps)
		Get values of multiple datapoints

	GetSetpoint(dp)
		Get value of single setpoint

	GetSetpoints(sps)
		Get values of multiple setpoints
	"""
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

	SPItem = namedtuple('SPItem', ['addr_r', 'addr_w', 'limits', 'scale'])
	SP = {
		'CO2.Avail': SPItem((16, 0), (42, 0), (0, 3), 1),
		'FilterChange': SPItem((18, 2), (652, 0), (0, 65535), 1.0/12),
		'EquipmentType': SPItem((5, 0), (20, 0), (0, 1), 1),
		'HotWater.E.Heating': SPItem((136, 0), (282, 0), (0, 1), 1),			# 0=off, 1=on
		'HotWater.Fast.Heating': SPItem((106, 0), (222, 0), (0, 1), 1),			# 0=off, 1=on
		'HotWater.Temperature': SPItem((129, 0), (268, 0), (20, 75), 0.01),
		'KWH.COP.Reset.Day': SPItem((15, 2), (646, 0), (0, 65535), 1),
		'KWH.COP.Reset.Month': SPItem((16, 2), (648, 0), (0, 65535), 1),
		'KWH.COP.Reset.Year': SPItem((17, 2), (650, 0), (0, 65535), 1),
		'OperatingMode.Holiday.Day': SPItem((2, 6), (936, 0), (0, 59), 1),
		'OperatingMode.Holiday.Month': SPItem((1, 6), (934, 0), (0, 23), 1),
		'OperatingMode.Holiday.Year': SPItem((0, 6), (932, 0), (0, 99), 1),
		'OperatingMode': SPItem((0, 0), (0, 10), (0, 9), 1),					# 0=off, 1=summer, 2=winter, 3=auto
		'Temperature.Normal': SPItem((10, 0), (30, 0), (10, 30), 0.01),
		'Temperature.ActiveCooling': SPItem((19, 0), (48, 0), (15, 40), 0.01),
		'ActiveCooling.Mode': SPItem((9, 0), (28, 0), (0, 2), 1),				# 0=off, 1=on, 2=eco
		'Ventilation.Level': SPItem((46, 0), (102, 0), (0, 4), 1),				# 0=auto, 1=level1, 2=level2, 3=level3, 4=level4
	}

	def __init__(self, device=None, user=None, passwd=None):
		"""
		Initialize communication with Pichler unit.

		Creates underlying Nabto communication client and establishes session to device.
		
		Parameters
		----------
		device : str, optional
			Device ID, by default None
		user : str, optional
			Name of account that should be used to access unit's data, by default None
		passwd : str, optional
			Password for given account, by default None

		If any of these parameters is not provided, value from `pichler.ini` file is used instead.
		"""
		package_dir = os.path.dirname(os.path.abspath(__file__))

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

	def GetDatapoint(self, dp):
		"""Get value of single datapoint
		
		Parameters
		----------
		dp : str
			Datapoint name (see `Pichler.DP` dict)

		Returns
		-------
		int, float
			Real value of datapoint (scaled appropriately)
		"""
		item = self.DP[dp]
		return self.DatapointRawReadValue(item.addr[0], item.addr[1]) * item.scale

	def GetDatapoints(self, dps):
		"""Get values of multiple datapoints
		
		Parameters
		----------
		dps : list
			List of datapoint names (see `Pichler.DP` dict)
		
		Returns
		-------
		list
			Real values of given datapoints (same order as input list)
		"""
		l = []
		for dp in dps:
			item = self.DP[dp]
			l.append([item.addr[0], item.addr[1]])
		r = self.DatapointRawReadListValues(l)
		for i in range(len(dps)):
			item = self.DP[dps[i]]
			r[i] = r[i] * item.scale
		return r

	def GetSetpoint(self, sp):
		"""Get value of single setpoint
		
		Parameters
		----------
		sp : str
			Setpoint name (see `Pichler.SP` dict)

		Returns
		-------
		int, float
			Real value of setpoint (scaled appropriately)
		"""
		item = self.SP[sp]
		return self.SetpointRawReadValue(item.addr_r[0], item.addr_r[1]) * item.scale

	def GetSetpoints(self, sps):
		"""Get values of multiple setpoints
		
		Parameters
		----------
		sps : list
			List of setpoint names (see `Pichler.SP` dict)
		
		Returns
		-------
		list
			Real values of given setpoints (same order as input list)
		"""
		l = []
		for sp in sps:
			item = self.SP[sp]
			l.append([item.addr_r[0], item.addr_r[1]])
		r = self.SetpointRawReadListValues(l)
		for i in range(len(sps)):
			item = self.SP[sps[i]]
			r[i] = r[i] * item.scale
		return r

	def RpcInvoke(self, command, params):
		"""
		Invoke RPC command to device
		
		Parameters and response data are defined in RPC interface file (`unabto_queries.xml` by default).

		Parameters
		----------
		command : str
			Command name
		params : str
			Request parameters (JSON)
		
		Returns
		-------
		dict
			Response from device
		"""
		r = self.session.RpcInvoke('nabto://%s/%s.json?%s' % (self.device, command, params))
		if r:
			return r['response']
		return []

	def Ping(self):
		"""
		Ping device and return its reponse
		
		Returns
		-------
		dict
			Device's response to ping
		"""
		return self.RpcInvoke('ping', 'ping=1885957735')

	def DatapointRawReadValues(self, address, obj, length):
		"""
		Read raw values from one or more (neighboring) datapoints
		
		Parameters
		----------
		address : int
			Address to read from
		obj : int
			Object to read from
		length : int
			Number of subsequent datapoints to read
		
		Returns
		-------
		list
			List of raw values read from given address
		"""
		response = self.RpcInvoke('datapointReadValue', 'address=%d&obj=%d&length=%d' % (address, obj, length))
		if response:
			return [i['value'] for i in response['data']]
		return []

	def DatapointRawReadValue(self, address, obj=0):
		"""
		Read raw value from single datapoint
		
		Parameters
		----------
		address : int
			Address to read from
		obj : int, optional
			Object to read from, by default 0
		
		Returns
		-------
		int
			Raw value read from given address
		"""
		return self.DatapointRawReadValues(address, obj, 1)[0]

	def DatapointRawReadListValues(self, lst):
		"""
		Read raw values from multiple datapoints
		
		Parameters
		----------
		lst : list
			List of [address, object] pairs of datapoints to read
		
		Returns
		-------
		list
			Raw values for each pair in original order
		"""
		l = [{'address': i[0], 'obj': i[1]} for i in lst]
		request = {'request': {'list': l}}
		response = self.RpcInvoke('datapointReadListValue', 'json=%s' % json.dumps(request))
		if response:
			return [i['value'] for i in response['data']]
		return []

	def SetpointRawReadValues(self, address, obj, length):
		"""
		Read raw values from one or more (neighboring) setpoints
		
		Parameters
		----------
		address : int
			Address to read from
		obj : int
			Object to read from
		length : int
			Number of subsequent setpoints to read
		
		Returns
		-------
		list
			List of raw values read from given address
		"""
		response = self.RpcInvoke('setpointReadValue', 'address=%d&obj=%d&length=%d' % (address, obj, length))
		if response:
			return [i['value'] for i in response['data']]
		return []

	def SetpointRawReadValue(self, address, obj=0):
		"""
		Read raw value from single setpoint
		
		Parameters
		----------
		address : int
			Address to read from
		obj : int, optional
			Object to read from, by default 0
		
		Returns
		-------
		int
			Raw value read from given address
		"""
		return self.SetpointRawReadValues(address, obj, 1)[0]

	def SetpointRawReadListValues(self, lst):
		"""
		Read raw values from multiple setpoints
		
		Parameters
		----------
		lst : list
			List of [address, object] pairs of setpoints to read
		
		Returns
		-------
		list
			Raw values for each pair in original order
		"""
		l = [{'address': i[0], 'obj': i[1]} for i in lst]
		request = {'request': {'list': l}}
		response = self.RpcInvoke('setpointReadListValue', 'json=%s' % json.dumps(request))
		if response:
			return [i['value'] for i in response['data']]
		return []
