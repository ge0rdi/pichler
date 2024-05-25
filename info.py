"""
Show basic runtime info from PKOM4 unit
"""

import pichler

device = pichler.Pichler()

print('Ping response: %s' % device.Ping())
print('')

print('Current temperature: %.2f C' % device.GetDatapoint('Temperature.Room'))
print('')

print('Power consumption')
pc_vent = device.GetDatapoint('Power.Ventilation')
pc_heat = device.GetDatapoint('Power.HeatPump')
pc_watr = device.GetDatapoint('Power.HotWater')
print('  Total            : %.1f W' % (pc_vent + pc_heat + pc_watr))
print('  Ventilation      : %.1f W' % pc_vent)
print('  Heat pump        : %.1f W' % pc_heat)
print('  Hot water        : %.1f W' % pc_watr)
print('')

print('Energy consumption')
print('  Total            : %d kWh' % device.GetDatapoint('Energy.Total'))
print('  Ventilation      : %d kWh' % device.GetDatapoint('Energy.Ventilation'))
print('  Heating          : %d kWh' % device.GetDatapoint('Energy.Heating'))
print('  Cooling          : %d kWh' % device.GetDatapoint('Energy.Cooling'))
print('  Hot water        : %d kWh' % device.GetDatapoint('Energy.HotWater'))
print('')

print('Air flow')
print('  Level            : %d'        % device.GetDatapoint('Ventilation.Level'))
print('  Supply           : %.2f m3/h' % device.GetDatapoint('Ventilation.Supply'))
print('  Extract          : %.2f m3/h' % device.GetDatapoint('Ventilation.Extract'))
print('  Balance          : %d%%' % device.SetpointRawReadValue(45, 0))
print('')

print('Air temperature')
print('  Supply           : %.2f C' % device.GetDatapoint('Temperature.Air.Supply'))
print('  Extract          : %.2f C' % device.GetDatapoint('Temperature.Air.Extract'))
print('  Outdoor          : %.2f C' % device.GetDatapoint('Temperature.Air.Outdoor'))
print('  Exhaust          : %.2f C' % device.GetDatapoint('Temperature.Air.Exhaust'))
print('')

print('Hot water')
print('  Center           : %.2f C' % device.GetDatapoint('Temperature.Water.Center'))
print('  Bottom           : %.2f C' % device.GetDatapoint('Temperature.Water.Bottom'))
print('')

print('Various')
status = device.GetDatapoint('StatusBits') & 0xffff
print('  Status bits      : %s'      % hex(status))
if status & 0x0001:
	print('                     Water heating')
if status & 0x0004:
	print('                     Heating')
if status & 0x0008:
	print('                     Cooling')
if status & 0x0040:
	print('                     Legionella protection')
if status & 0x0100:
	print('                     E-booster')
if status & 0x0200:
	print('                     E-heating')
if status & 0x2000:
	print('                     Defrost')

print('  CO2 level        : %d ppm'  % device.GetDatapoint('CO2'))
malfunction = device.GetDatapoint('Malfunction')
print('  Malfunction      : %d'      % malfunction)
if (malfunction == 256):
	print('                     Defrost time exceeded')
if (malfunction == 16384):
	print('                     4way valve error')
print('  Filter change    : %d days' % device.GetSetpoint('FilterChange'))
print('  SCOP             : %.2f'    % device.GetDatapoint('SCOP'))
print('  HP COP           : %.2f'    % device.GetDatapoint('HP.COP'))
print('  HP heating power : %d W'    % device.GetDatapoint('HP.HeatingPower'))
