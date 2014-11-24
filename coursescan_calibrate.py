#!/usr/bin/env python
#from numpy import *
#from matplotlib.pyplot import *

from time import sleep
from datetime import datetime

# use argparse module to read commandline options
import argparse

pars = argparse.ArgumentParser(description="""
scans newfocus piezo using lasernet.  takes data at piezo offsets.
""")

pars.add_argument("--start", default=765, type=float, help="piezo start")
pars.add_argument("--stop", default=781, type=float, help="piezo stop")
pars.add_argument("--step", default=0.5, type=float, help="piezo step")

pars.add_argument("--daq", help="channel to take nidaq data")

pars.add_argument("--laser", default="localhost", help="set lasernet address")
pars.add_argument("-w", "--wave", default=None, help="wavelength meter address")

args = pars.parse_args()




#
# lasernet client (through websockets)
#

import labdrivers.websocks
laser = labdrivers.websocks.LaserClient(args.laser)

#
# Wavelength Meter
#

import labdrivers.rvisa
wlm = labdrivers.rvisa.WlMeter(args.wave)


#
# DAQ
#

import labdrivers.daq
daq = labdrivers.daq.SimpleDaq(args.daq, 5000, 100, maxv=10.)



def stepto(a, b, d):
    d = abs(d) if b > a else -abs(d)
    yield a
    while abs(b - a) > abs(d):
        a += d
        yield a
    yield b


import numpy

wls = numpy.array(list(stepto(args.start, args.stop, args.step)))
wlms = numpy.empty_like(wls)
trans = numpy.empty_like(wls)

for i, wl in enumerate(wls):
    laser.set_wave(wl)
    wlms[i] = wlm.wl()
    trans[i] = numpy.mean(daq.read())
    print("%s %s %s" % (wl, wlms[i], trans[i]))


from datetime import datetime
fname = datetime.now().strftime("%y.%m.%d_%H%M%S") + "_courscan_calibrate.npy"
print("saving to %s" % fname)
numpy.save(fname, numpy.vstack((wls, wlms, trans)).T)

