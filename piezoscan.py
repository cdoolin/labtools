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

pars.add_argument("start", default=0.5, type=float, help="piezo start")
pars.add_argument("stop", default=0.5, type=float, help="piezo stop")
pars.add_argument("step", default=0.5, type=float, help="piezo step")

pars.add_argument("--laser", default="localhost", help="set lasernet address")
pars.add_argument("--daq", action='append', help="channel to take nidaq data")
#pars.add_argument("-s", "--sa", default=None, help="specify SA server to save with")
pars.add_argument("-w", "--wave", default=None, help="wavelength meter address")
pars.add_argument("--waveskip", default=20, type=int, help="take wavelength readings every nth step (default: 5)")
#pars.add_argument("-m", "--megadaq", default=None, help="megadaq address")

#pars.add_argument("-P", "--noplot", action='store_true', help="disable plotting at end of scan")
pars.add_argument("-s", "--save", action='store_true', help="enable saving")
pars.add_argument("-p", "--plot", default=False, action='store_true', help="plot results")
pars.add_argument("--maxv", default=10., type=float, help="daq volt range")

args = pars.parse_args()

#
# list of functions to take data with at each piezo point
#
def data(func):
    data.s.append(func)
    return func
data.s = []
    
#
# lasernet client (through websockets)
#

import labdrivers.websocks
laser = labdrivers.websocks.LaserClient(args.laser)

@data
def set_piezo(pz):
    laser.set_volt(pz)
    sleep(.01)
    return pz

#
# daq
#

if args.daq is not None:
    import labdrivers.daq
    
    def make_read_daq(daq):
        container = [None]

        def volts_mean(pz):
            container[0] = daq.read()
            return container[0].mean()

        def volts_std(pz):
            return container[0].std()

        return [volts_mean, volts_std]

    for channel in args.daq:
        daq = labdrivers.daq.SimpleDaq(channel, 5000, 100, maxv=args.maxv)
        data.s += make_read_daq(daq)
    

#
# Wavelength Meter
#

if args.wave is not None:
    import labdrivers.rvisa
    wlm = labdrivers.rvisa.WlMeter(args.wave)
    @data
    def read_wlm(pz):
        if (pz - args.start) / args.step % args.waveskip == 0:
            return wlm.wl()
        else:
            return 0

#
#
#

def stepto(a, b, d):
    d = abs(d) if b > a else -abs(d)
    yield a
    while abs(b - a) > abs(d):
        a += d
        yield a
    yield b


laser.set_volt(args.start)
sleep(.1)

results = []
for pz in stepto(args.start, args.stop, args.step):
    results.append([f(pz) for f in data.s])
    print results[-1]
    

if args.save:
    import numpy
    fname = datetime.now().strftime("%y.%m.%d_%H%M%S") + "_pzscan.txt"
    print("saving to %s" % fname)
    numpy.savetxt(fname, numpy.array(results))

if args.plot and len(data.s) > 1:
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot([r[0] for r in results], [r[1] for r in results])
    plt.show(block=True)
