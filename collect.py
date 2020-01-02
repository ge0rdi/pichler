"""
Periodically read selected data from heat pump unit and store them to Influx database.

Read data is stored to DB:
* when its value has changed since previous reading
* every hour

InfluxDb config is taken from `collect.ini` file.
"""

import os
import pichler
import time
from influxdb import InfluxDBClient
try:
	import configparser
except:
	# python2 compatibility
	import ConfigParser
	configparser = ConfigParser

def Log(s):
	print('[%s] %s' % (time.ctime(time.time()), s))

# datapoints to read
data_points = [
	'Energy.Total',
	'Energy.Cooling',
	'Energy.Heating',
	'Energy.HotWater',
	'Energy.Ventilation',

	'Power.HotWater',
	'Power.HeatPump',
	'Power.Ventilation',

	'Temperature.Room',
	'Temperature.Air.Supply',
	'Temperature.Air.Extract',
	'Temperature.Air.Outdoor',
	'Temperature.Air.Exhaust',
	'Temperature.Water.Center',
	'Temperature.Water.Bottom',

	'Ventilation.Level',
	'Ventilation.Supply',
	'Ventilation.Extract',

	'StatusBits',
	'CO2',
]

# `StatusBits` will be stored as individual bits rather than raw value
status_bits = [
	{
		'mask': 1,
		'name': 'Status.HotWater',
	},
	{
		'mask': 4,
		'name': 'Status.Heating',
	}
]

Log('Started collecting data')

package_dir = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read(os.path.join(package_dir, 'collect.ini'))

# Influx database client
influx = InfluxDBClient(config.get('influxdb', 'host'), config.getint('influxdb', 'port'), config.get('influxdb', 'username'), config.get('influxdb', 'password'), config.get('influxdb', 'database'))

# Pichler device client
device = pichler.Pichler()

prev = [0] * len(data_points)
power_total_prev = 0
minutes = 0

data = []

while True:
	current_time = int(time.time())

	# read actual values
	values = device.GetDatapoints(data_points)

#	print(values)

	# select values to report
	report = [False] * len(data_points)

	for i in range(len(data_points)):
		# value should be reported if it was changed or timeout exceeded
		if (values[i] != prev[i]) or ((minutes % 60) == 0):
			report[i] = True

	def AddMeasurement(name, value):
		m = {'measurement': name.replace('.', '_'), 'time': current_time, 'fields': {'value': value}}
		data.append(m)

	# report values
	for i in range(len(data_points)):
		if report[i]:
			val = values[i]

			# special handling for StatusBits
			# report each bit separately
			if data_points[i] == 'StatusBits':
				for d in status_bits:
					val = 1 if (values[i] & d['mask']) != 0 else 0
					AddMeasurement(d['name'], val)
				continue

			AddMeasurement(data_points[i], val)

	# get total power consumption (accumulate all power comsumption values)
	power_total = 0
	for i in range(len(data_points)):
		if data_points[i].startswith('Power.'):
			power_total += values[i]

	# report if changed
	if power_total != power_total_prev:
		AddMeasurement('Power.Total', power_total)

	if data:
#		print(data)
		try:
			# try to write data to database
			# empty data on success (we don't need them anymore)
			# otherwise keep them, so we'll try to write them on next occasion
			if influx.write_points(data, time_precision='s'):
				data = []
		except Exception as e:
			Log('Unexpected error: ' + str(e))

	# store previous values
	prev = values
	power_total_prev = power_total

	# wait a minute
	time.sleep(60)
	minutes += 1
