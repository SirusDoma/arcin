#!/usr/bin/env python

import struct

from hidapi import hidapi
import ctypes

hiddev = hidapi.hid_open(0x1d50, 0x6080, None)
	
if not hiddev: 
	raise RuntimeError('Target not found.')

prev = None

s = struct.Struct('<xxxHH')

while 1:
	data = ctypes.create_string_buffer(s.size)
	if hidapi.hid_read(hiddev, data, s.size) != s.size:
		raise RuntimeError('Reading failed.')
	
	x, y = s.unpack(data)
	x = x >> 6
	y = y >> 6
	data = x, y
	if prev != data:
		print data
		prev = data