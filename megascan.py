#!/usr/bin/env python
from numpy import *

import labdrivers

from time import sleep
from datetime import datetime

# use argparse module to read commandline options
import argparse

pars = argparse.ArgumentParser(description="""
scans wavelength with santec laser and collects megadaqtyl data 
and dc transmission (nidaq) data.
""")

pars.add_argument("start", type=float, help="start wavelength")
pars.add_argument("stop", type=float, help="stop wavelength")
pars.add_argument("step", type=float, help="takes data every step wavelength")

pars.add_argument("-l", "--laser", type=str, default="127.0.0.1",
    help="location of scantech server")

pars.add_argument("-c", "--channel", type=str, default="/dev1/ai0",
    help="nidaqmx channel (default: /dev1/ai0)")

pars.add_argument("-m", "--megadaq", type=str, default="",
    help="megadaq location, unspecified means don't use it")
pars.add_argument("-p", "--plot", action='store_true', default=False,
    help="plot transmission after the scan")
args = pars.parse_args()


# initialize drivers
# scantech client (through websockets)
l = labdrivers.ScantechClient(args.laser)

# nidaq
d = labdrivers.SimpleDaq(args.channel, 10000, 100, minv=0., maxv=10.)

#
# megadaqtyl.  really simple so implement right here.
#
if len(args.megadaq) > 0:
    import zmq
    
    context = zmq.Context()
    s = context.socket(zmq.REQ)
    print("connecting to megadaq at %s" % args.megadaq)
    s.connect("tcp://%s:6497" % args.megadaq)
    print("connected.")
    
    def acquire(desc):
        s.send("acquire;%s" % desc)
        s.recv()
else:
    def acquire(d):
        pass
# end magadaq driver


# wavelengths.  santec laser has set prcision of 1 pm.
waves = arange(args.start, args.stop, args.step).round(decimals=3)

l.set_wave(waves[0])
sleep(.1)

avgs = zeros_like(pz)
stds = zeros_like(pz)

# save data
fname = datetime.now().strftime("%y.%m.%d_%H%M%S") + "_megascan.txt"
f = open(fname, "w")

print("saving to %s..." % fname)

# save transmission so can plot later
trans = zeros_like(waves)
# use enough padding 0s
fmt = "%0" + str(len(waves) / 10 + 1) + "d"
# loop through wavelengths and measure at each one
for i, w in enumerate(waves):
    l.set_wave(wave)
    sleep(.05)
    
    trans1 = d.read()
    acquire(fmt % i)
    trans2 = d.read()
    tran = concatenate((trans1, trans2))
    trans[i] = mean(trans)
    f.write("%d\t%.3f\t%e\t%e\t" % (i, w, trans[i], std(tran)))

# plot results
if args.plot:
    print("plotting...")
    from matplotlib.pyplot import *
    figure()
    plot(waves, trans)
    xlabel("Wavelength (nm)")
    ylabel("Transmission (V)")
    show(block=True)

