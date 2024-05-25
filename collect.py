"""
Periodically read selected data from heat pump unit
"""

import os
import pichler
import time
import traceback
import paho.mqtt.client as mqtt

debug = False

MQTT_PREFIX = 'pkom4/'

def Log(s):
	print('[%s] %s' % (time.ctime(time.time()), s))
def DebugLog(s):
	if debug:
		Log(s)

set_points = [
	('setting/water/temperature', 'HotWater.Temperature'),
	('setting/water/e-heating', 'HotWater.E.Heating'),
	('setting/water/fast-heating', 'HotWater.Fast.Heating'),
	('setting/ventilation/temperature/normal', 'Temperature.Normal'),
	('setting/ventilation/temperature/cooling', 'Temperature.ActiveCooling'),
	('setting/operating-mode', 'OperatingMode'),
]

# datapoints to read
data_points = [
	('energy', 'Energy.Total'),
	('energy/cooling', 'Energy.Cooling'),
	('energy/heating', 'Energy.Heating'),
	('energy/water', 'Energy.HotWater'),
	('energy/ventilation', 'Energy.Ventilation'),

#	('power', ''),  # sum of items below
	('power/heat-pump', 'Power.HeatPump'),
	('power/water', 'Power.HotWater'),
	('power/ventilation', 'Power.Ventilation'),

	('water/temperature/center', 'Temperature.Water.Center'),
	('water/temperature/bottom', 'Temperature.Water.Bottom'),

	('ventilation/temperature/room', 'Temperature.Room'),
	('ventilation/temperature/supply', 'Temperature.Air.Supply'),
	('ventilation/temperature/extract', 'Temperature.Air.Extract'),
	('ventilation/temperature/outdoor', 'Temperature.Air.Outdoor'),
	('ventilation/temperature/exhaust', 'Temperature.Air.Exhaust'),
	('ventilation/level', 'Ventilation.Level'),
	('ventilation/volume/supply', 'Ventilation.Supply'),
	('ventilation/volume/extract', 'Ventilation.Extract'),

	('co2', 'CO2'),
	('status', 'StatusBits'),  # split into status/xyz bits below
]

# `StatusBits` will be stored as individual bits rather than raw value
status_bits = [
	{
		'mask': 0x0001,
		'name': 'status/water',
	},
	{
		'mask': 0x0004,
		'name': 'status/heating',
	},
	{
		'mask': 0x0008,
		'name': 'status/cooling',
	},
	{
		'mask': 0x0200,
		'name': 'status/fast-heating',
	}
]

# Pichler device client
device = pichler.Pichler()

def on_connect(client, userdata, flags, reason_code, properties):
	DebugLog(f"on_connect: {reason_code}, {flags}")
	for m in set_points:
		client.subscribe(MQTT_PREFIX + m[0] + '/set')

def on_message(client, userdata, msg):
	DebugLog(f"on_message: {msg.topic}")
	for m in set_points:
		if msg.topic == (MQTT_PREFIX + m[0] + '/set'):
			try:
				Log(msg.topic + " " + msg.payload.decode())
				if not debug:
					device.SetSetpoint(m[1], float(msg.payload))
			except Exception as e:
				Log('Error in SetSetpoint: ' + str(e))
				traceback.print_exc()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

mqtt_host = os.environ['MQTT_HOST']
mqtt_port = os.environ.get('MQTT_PORT', '1883')

Log("Connecting to MQTT")

while True:
	try:
		client.connect(mqtt_host, int(mqtt_port), 60)
		break
	except Exception as e:
		Log('MQTT connect: ' + str(e))
	time.sleep(10)

client.loop_start()

Log('Collecting data')

while True:

	try:
		def Publish(name, value):
			if not debug:
				client.publish(MQTT_PREFIX + name, value)
			else:
				DebugLog(f"publish: {name} = {value}")

		# publish data to MQTT
		for m in set_points:
			Publish(m[0], device.GetSetpoint(m[1]))

		# read actual values
		values = device.GetDatapoints([d[1] for d in data_points])

		# report values
		for i in range(len(data_points)):
			val = values[i]

			# special handling for StatusBits
			# report each bit separately
			if data_points[i][0] == 'status':
				for d in status_bits:
					bval = 1 if (values[i] & d['mask']) != 0 else 0
					Publish(d['name'], bval)

			Publish(data_points[i][0], val)

		# get total power consumption (accumulate all power comsumption values)
		power_total = 0
		for i in range(len(data_points)):
			if data_points[i][0].startswith('power/'):
				power_total += values[i]

		Publish('power', power_total)

	except:
		Log('Unexpected error:')
		traceback.print_exc()

	# wait a minute
	time.sleep(60)
