from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import time
from picoscope import ps2000
from picoscope import ps2000a
import pylab as plt
import numpy as np

def run_ps():
	
	# global ps
	ps = ps2000a.PS2000a()

	channelRange = ps.setChannel('A', 'DC', 2.0, 0.0, enabled=True,
								 BWLimited=False)
	channelRange = ps.setChannel('B', 'DC', 10.0, 0.0, enabled=True,
								 BWLimited=False)
	# print("Chosen channel range = %d" % channelRange)

	ps.setSimpleTrigger('B', -4.0, 'Falling', delay=0, timeout_ms=100, enabled=True)

	return ps

def close_ps(ps):
	ps.stop()
	ps.close()