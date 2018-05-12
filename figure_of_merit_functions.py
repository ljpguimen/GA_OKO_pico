
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import time
from picoscope import ps2000
from picoscope import ps2000a
import pylab as plt
import numpy as np


def test_genes(ps):
	# print(__doc__)

	# print("Attempting to open Picoscope 2000...")

	# ps = ps2000.PS2000()
	# Uncomment this line to use with the 2000a/2000b series
	# ps = ps2000a.PS2000a()

	# print("Found the following picoscope:")
	# print(ps.getAllUnitInfo())


	# waveform_desired_duration = 0.05
	waveform_desired_duration = 1e-4
	obs_duration = 3 * waveform_desired_duration
	sampling_interval = obs_duration / 4096

	(actualSamplingInterval, nSamples, maxSamples) = \
		ps.setSamplingInterval(sampling_interval, obs_duration)
	# print("Sampling interval = %f ns" % (actualSamplingInterval * 1E9))
	# print("Taking  samples = %d" % nSamples)
	# print("Maximum samples = %d" % maxSamples)

	# the setChannel command will chose the next largest amplitude
	# channelRange = ps.setChannel('A', 'DC', 2.0, 0.0, enabled=True,
	# 							 BWLimited=False)
	# channelRange = ps.setChannel('B', 'DC', 10.0, 0.0, enabled=True,
	# 							 BWLimited=False)
	# # print("Chosen channel range = %d" % channelRange)

	# ps.setSimpleTrigger('B', -4.0, 'Falling', delay=0, timeout_ms=100, enabled=True)

	# ps.setSigGenBuiltInSimple(offsetVoltage=0, pkToPk=1.2, waveType="Sine",
	# 						  frequency=50e3)

	# ps.runBlock()
	# ps.waitReady()
	# # print("Waiting for awg to settle.")
	# time.sleep(0)
	ps.runBlock()
	ps.waitReady()
	# print("Done waiting for trigger")
	dataA = ps.getDataV('A', nSamples, returnOverflow=False)
	# dataB = ps.getDataV('B', nSamples, returnOverflow=False)


	# dataTimeAxis = np.arange(nSamples) * actualSamplingInterval

	# ps.stop()
	# ps.close()

	# Uncomment following for call to .show() to not block
	# plt.ion()
	
	print (np.absolute(dataA).mean())
	# print (np.absolute(dataB).mean())
	return np.absolute(dataA).mean()
	
