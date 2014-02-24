#!/usr/bin/env python
from numpy import *

import labdrivers
from time import sleep, time
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

# wl meter
w = labdrivers.WlMeter()
if not w.ok():
    print("couldn't connect to wavelength meter")
    
# nidaq
d = labdrivers.SimpleDaq(args.channel, 10000, 100, minv=0., maxv=10.)

# SA
s = labdrivers.SA()
if not w.ok():
    print("couldn't connect to sa")
s.endsave()


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
fts = arange(args.start, args.stop, args.step).round(decimals=2)

# Fine tune points to take wlmeter readings at
n= 20. #number of points (needs to be float) 
wls = arange(n+1)*200./n-100 #arranges them on -100 to 100


l.set_fine(fts[0])
sleep(.1)

avgs = zeros_like(fts)
stds = zeros_like(fts)
wlrs = zeros_like(fts)

# save data
fname = datetime.now().strftime("%y.%m.%d_%H%M%S") + "_finescan.txt"
file = open(fname, "w")

print("saving to %s" % fname)
print("scanning...")

# save transmission so can plot later
trans = zeros_like(fts)
wavel = zeros_like(fts)
# use enough padding 0s
fmt = "%0" + str(len(fts) / 10 + 1) + "d"
# define start time of scanning procedure
stt = time()

# loop through wavelengths and measure at each one
for i, f in enumerate(fts):
    #Time information
    t = time()-stt
    print t
    l.set_fine(f)
    sleep(0.05)
    trans1 = d.read()
    acquire(fmt % i)
    trans2 = d.read()
    tt = concatenate((trans1, trans2))
    trans[i] = mean(tt)
    
    if f in wls:
        wlrs[i] = w.wl()
    else:
        wlrs[i] = 0
    file.write("%d\t%.3f\t%e\t%e\t%.5f\t%e\n" % (i, f, trans[i], std(tt), t, wlrs[i]))

file.close()

# plot results
if args.plot:
    print("plotting...")
    from matplotlib.pyplot import *
    figure()
    plot(fts, trans,'c.')
    xlabel("Fine Tuning (nm)")
    ylabel("Transmission (V)")
    show(block=True)

