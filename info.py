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
print('  Status bits      : %s'      % hex(device.GetDatapoint('StatusBits') & 0xffff))
print('  CO2 level        : %d ppm'  % device.GetDatapoint('CO2'))
print('  Malfunction      : %d'      % device.GetDatapoint('Malfunction'))
print('  Filter change    : %d days' % (device.SetpointRawReadValue(18, 2) / 12))
print('  SCOP             : %.2f'    % device.GetDatapoint('SCOP'))
print('  HP COP           : %.2f'    % device.GetDatapoint('HP.COP'))
print('  HP heating power : %d W'    % device.GetDatapoint('HP.HeatingPower'))
