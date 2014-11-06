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

pars.add_argument("-m", "--mode", type=float, help="course start wavelengths to scan from")

pars.add_argument("--laser", default="localhost", help="set lasernet address")
pars.add_argument("--daq", action='append', help="channel to take nidaq data")
#pars.add_argument("-s", "--sa", default=None, help="specify SA server to save with")
pars.add_argument("-w", "--wave", default=None, help="wavelength meter address")
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
        daq = labdrivers.daq.SimpleDaq(channel, 5000, 40, maxv=args.maxv)
        data.s += make_read_daq(daq)
    

#
# Wavelength Meter
#

if args.wave is not None:
    import labdrivers.rvisa
    wlm = labdrivers.rvisa.WlMeter(args.wave)
    def get_wl():
        return wlm.wl()
else:
    def get_wl():
        return 0


def stepto(a, b, d):
    d = abs(d) if b > a else -abs(d)
    yield a
    while abs(b - a) > abs(d):
        a += d
        yield a
    yield b


pzs = list(stepto(args.start, args.stop, args.step))

import numpy

def scan_and_save():
    laser.set_volt(args.start)
    sleep(.1)

    if wlm is not None:
        wl = wlm.wl()

    results = numpy.empty((len(pzs), len(data.s)))
    for i, pz in enumerate(pzs):
        results[i, :] = numpy.array([f(pz) for f in data.s])

    fname = datetime.now().strftime("%y.%m.%d_%H%M%S") + "_wl%s_pzscan.npy" % str(wl)
    numpy.save(fname, results)
    print fname


#
#  Main Loop.  Use windows only call to check for a keypress.
#

#import os
import msvcrt

laser.set_volt(0)
sleep(.1)

if args.mode is not None:
    print("setting wavelength to %s nm" % args.mode)
    laser.set_wave(args.mode)

while True:
    if msvcrt.kbhit() > 0:
        c = msvcrt.getch()
        if c == 'p':
            print("paused..")
            msvcrt.getch()
            print("resumed")
        elif c == 'a':
            print('a pressed')
        else:
            break;
    scan_and_save()

# while msvcrt.kbhit() < 1:
#    scan_and_save()

msvcrt.getch()

