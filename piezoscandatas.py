#!/usr/bin/env python
from numpy import *
from matplotlib.pyplot import *

import labdrivers

from time import sleep
from datetime import datetime

# use argparse module to read commandline options
import argparse

pars = argparse.ArgumentParser(description="""
scans laser wavelength by setting piezo voltage. 
communicates through lasernet so the lasernet server must be running. 
reads volt (transmission) from channel /Dev1/ai2 of a ni daq card.
""")

pars.add_argument("step", default=0.5, type=float, help="volt stepsize to take measurements at")
pars.add_argument("-l", "--lower", type=float, default=1., help="set lower volt")
pars.add_argument("-u", "--upper", type=float, default=100., help="set upper volt")
pars.add_argument("-r", "--reverse", action='store_true', help="scan in reverse")
pars.add_argument("-P", "--noplot", action='store_true', help="disable plotting at end of scan")
pars.add_argument("-s", "--sa", action='store', help="specify SA server to save with")
pars.add_argument("-m", "--megadaq", action='store', help="specify megadaq server to save with")
pars.add_argument("-W", "--nowavelength", default=False, action='store_true', help="don't use wavelength meter")
pars.add_argument("-S", "--nosave", action='store_true', help="disable saving")
pars.add_argument("-o", "--outfile", default="", help="save data to OUTFILE")
pars.add_argument("--channel", default="Dev1/ai2", help="set nidaq channel to read")
pars.add_argument("--laser", default="localhost", help="set lasernet address")

args = pars.parse_args()


#
# megadaq driver
#
if args.megadaq is not None:
    print("saving megadata at %s" % args.megadaqtyl)
    import zmq
    
    context = zmq.Context()
    s = context.socket(zmq.REQ)
    s.connect("tcp://%s:6497" % args.megadaq)
    
    def megasave(desc):
        s.send("acquire;%s" % desc)
        s.recv()
else:
    def megasave(d):
        pass
# end megadaq driver


#
# SA
#
if not args.sa:
    # hackity hack hack
    labdrivers.SA = labdrivers.SAMock

s = labdrivers.SA()
s.endsave()
# end sa 

# otehr drivers
# lasernet client (through websockets)
l = labdrivers.LaserClient(args.laser)
# wl meter
w = labdrivers.WlMeter()
if not w.ok():
    print("couldn't connect to wavelength meter")
# nidaq
d = labdrivers.SimpleDaq(args.channel, 10000, 100, minv=0., maxv=10.)
# SA


#
# setup scan parameters
#

# piezo volts to take measurements at
pz = arange(args.lower, args.upper, args.step).round(1)
if not args.reverse:
    pz = pz[::-1]

# volts to take wlmeter readings at
#wls = arange(11)*10. # every 10 V
wls = pz[::len(pz)/10]

# set volt to initial setpoint
#l.set_volt(pz[0])
l.set_volt(100)
sleep(.5)

avgs = zeros_like(pz)
stds = zeros_like(pz)
wlrs = zeros_like(pz)

print("scanning...")

#
# scan!
# loop through volts and measure at each one
#
for i in range(len(pz)):
    l.set_volt(pz[i])
    sleep(.05)
    
    trans1 = d.read()

    #save sa and or megadaq
    s.save(1, i)
    megasave(i)

    if not args.nowavelength and pz[i] in wls:
        wlrs[i] = w.wl()
    else:
        wlrs[i] = 0

    trans2 = d.read()

    avgs[i] = mean(r_[trans1, trans2])
    stds[i] = std(r_[trans1, trans2])
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

