#!/usr/bin/env python

from hidapi import hidapi
from elftools.elf.elffile import ELFFile

import ctypes, time, sys

e = ELFFile(open(sys.argv[1]))

buf = ''

hid_arcin = 0x1d50
pid_arcin = 0x6080

hid_nemsys = 0x1ccf
pid_nemsys = 0x101c

pid_bootloader = 0x6084

for segment in sorted(e.iter_segments(), key = lambda x: x.header.p_paddr):
	if segment.header.p_type != 'PT_LOAD':
		continue
	
	data = segment.data()
	lma = segment.header.p_paddr
	
	# Workaround for LD aligning segments to a larger boundary than 8k.
	if lma == 0x8000000:
		lma += 0x2000
		data = data[0x2000:]
	
	# Add padding if necessary.
	buf += '\0' * (lma - 0x8002000 - len(buf))
	
	buf += data

# Align to 64B
if len(buf) & (64 - 1):
	buf += '\0' * (64 - (len(buf) & (64 - 1)))

# Open device
dev = hidapi.hid_open(hid_arcin, pid_bootloader, None)

if not dev:
	# Perhaps device is not in bootloader menu
	dev = hidapi.hid_open(hid_arcin, pid_arcin, None)

	# Ignore runtime nemsys mode, otherwise my real nemsys might get flashed accidentally lol
	if not dev: 
		raise RuntimeError('Device not found.')
	
	print 'Found runtime device, resetting to bootloader.'
	
	# Reset bootloader
	if hidapi.hid_send_feature_report(dev, ctypes.c_char_p('\x00\x10'), 2) != 2:
		raise RuntimeError('Reset failed.')
	
	time.sleep(1)
	
	hidapi.hid_exit()
	
	dev = hidapi.hid_open(hid_arcin, pid_bootloader, None)
	
	if not dev: 
		raise RuntimeError('Device not found.')

print 'Found bootloader device, starting flashing.'

# Prepare
if hidapi.hid_send_feature_report(dev, ctypes.c_char_p('\x00\x20'), 2) != 2:
	raise RuntimeError('Prepare failed.')

# Flash
while buf:
	if hidapi.hid_write(dev, ctypes.c_char_p('\x00' + buf[:64]), 65) != 65:
		raise RuntimeError('Writing failed.')
	buf = buf[64:]

# Finish
if hidapi.hid_send_feature_report(dev, ctypes.c_char_p('\x00\x21'), 2) != 2:
	raise RuntimeError('Finish failed.')

print 'Flashing finished, resetting to runtime.'

# Reset
if hidapi.hid_send_feature_report(dev, ctypes.c_char_p('\x00\x11'), 2) != 2:
	raise RuntimeError('Reset failed.')

time.sleep(1)

hidapi.hid_exit()

if hidapi.hid_open(hid_arcin, pid_arcin, None):
	print 'Done, everything ok.'
	
elif hidapi.hid_open(hid_arcin, pid_bootloader, None):
	print 'Still in bootloader mode.'

else:
	print 'Device disconnected.'
