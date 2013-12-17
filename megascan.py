#!/usr/bin/env python
from numpy import *
from matplotlib.pyplot import *

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

pars.add_argument("-b", "--blocks", type=float, default=1.,
    help="number of blocks to record with megadaq (default 1)")
args = pars.parse_args()


# initialize drivers
# scantech client (through websockets)
l = labdrivers.LaserClient(args.laser)

# nidaq
d = labdrivers.SimpleDaq(args.channel, 10000, 100, minv=0., maxv=10.)

# wavelengths 
pz = arange(args.start, args.stop, args.step)

l.set_wave(pz[0])
sleep(.5)

avgs = zeros_like(pz)
stds = zeros_like(pz)
wlrs = zeros_like(pz)

print("scanning..." )

# loop through volts and measure at each one
for i in range(len(pz)):
    l.set_volt(pz[i])
    sleep(.05)
    
    trans = d.read()
    avgs[i] = mean(trans)
    stds[i] = std(trans)

    s.save(1, i)

    if not args.nowavelength and pz[i] in wls:
        wlrs[i] = w.wl()
    else:
        wlrs[i] = 0
s.endsave()


# save data
if not args.nosave:
    if len(args.outfile) > 0:
        fname = args.outfile
    else:
        fname = datetime.now().strftime("%y.%m.%d_%H%M%S") + "_pzscan.txt"
    print("saving to %s..." % fname)

    with open(fname, "w") as f:
        for i in range(len(pz)):
            if wlrs[i] != 0:
                f.write("%d\t%e\t%e\t%e\t%e\n" % (i, pz[i], avgs[i], stds[i], wlrs[i]))
            else:
                f.write("%d\t%e\t%e\t%e\tInf\n" % (i, pz[i], avgs[i], stds[i]))
                

# plot results
if not args.noplot:
    print("plotting...")
    figure()
    plot(pz, avgs)
    xlabel("piezo %")
    ylabel("transmission (V)")
    show(block=True)

