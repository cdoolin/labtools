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
pars.add_argument("-v", "--maxv", type=float, action='store', default=10., help="set daq input voltage (default: 10)")
pars.add_argument("--channel", default="Dev1/ai0", help="set nidaq channel to read")
pars.add_argument("--laser", default="localhost", help="set lasernet address")


args = pars.parse_args()


#
# megadaq driver
#
if args.megadaq is not None:
    print("saving megadata at %s" % args.megadaq)
    import zmq
    
    context = zmq.Context()
    s = context.socket(zmq.REQ)
    server = "tcp://%s:6497" % args.megadaq
    s.connect(server)
    print("connected to %s" % server)
    def megasave(desc):
        print "sending save command"
        s.send("acquire;%s" % desc)
        s.recv()
        print("save ok")
else:
    def megasave(d):
        pass
# end megadaq driver


#
# SA
#

if args.sa:
    import labdrivers.zmqq
    s = labdrivers.zmqq.SA()
    s.endsave()
    def save_sa(i):
        s.save(1, i)
if not args.sa:
    def save_sa(i):
        pass

# end sa 

# otehr drivers
# lasernet client (through websockets)
import labdrivers.websocks
l = labdrivers.websocks.LaserClient(args.laser)

# wl meter
if args.nowavelength:
    def get_wl():
        return 0
else:
    import labdrivers.rvisa
    w = labdrivers.rvisa.WlMeter("GPIB0::4")

    def get_wl():
        return w.wl()

# nidaq
import labdrivers.daq
d = labdrivers.daq.SimpleDaq(channel=args.channel, rate=20000, n=400, maxv=args.maxv)
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
    save_sa(i)
    megasave(i)

    if pz[i] in wls:
        wlrs[i] = get_wl()
    else:
        wlrs[i] = 0


    trans2 = d.read()

    avgs[i] = mean(r_[trans1, trans2])
    stds[i] = std(r_[trans1, trans2])
if args.sa:
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
    plot(pz, avgs, 'ko')
    plot(pz, avgs, 'k--')
    xlabel("piezo %")
    ylabel("transmission (V)")
    show(block=True)

