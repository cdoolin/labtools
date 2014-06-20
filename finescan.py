#!/usr/bin/env python
from numpy import *

#import labdrivers
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
    help="location of scantech server (default: localhost)")
pars.add_argument("-s", "--save", action='store_true', default=False)
pars.add_argument("-r", "--reverse", action='store_true', default=False,
    help="scan in reverse")
	
pars.add_argument("-c", "--channel", type=str, default="/dev1/ai0",
    help="nidaqmx channel (default: /dev1/ai0)")

pars.add_argument("-m", "--megadaq", action='store_true', default=False,
    help="use megadaq, unspecified means don't use it")
pars.add_argument("-p", "--plot", action='store_true', default=False,
    help="plot transmission after the scan")
pars.add_argument("-v", "--volt", type=float, default=10., help="volt range for NI DAQ (default: 10 V)")
pars.add_argument("-f", "--fname", type=str, default="finescan")

pars.add_argument("--nodaq", "-D", action="store_true",
    help="disable collecting data with NI DAQ")

args = pars.parse_args()


# initialize drivers
# scantech client (through websockets)
from labdrivers.websocks import ScantechClient
l = ScantechClient(args.laser)

# nidaq
if args.nodaq:
    d = None
else:
    vv = args.volt
    from labdrivers.daq import SimpleDaq
    d = SimpleDaq(args.channel, 10000, 5, maxv=vv)

#
# megadaqtyl.  really simple so implement right here.
#
if args.megadaq:
	import zmq
    
	context = zmq.Context()
	s = context.socket(zmq.REQ)
	SERVER = "142.244.195.14"
	print("connecting to megadaq at %s" % SERVER)
	s.connect("tcp://%s:6497" % SERVER)
	print("connected.")
    
	def acquire(desc):
		s.send("acquire;%s" % desc)
		s.recv()
else:
    def acquire(d):
        pass
# end magadaq driver


# wavelengths.  santec laser has set prcision of 1 pm.
if args.reverse:
	fts = arange(args.stop, args.start, -1*args.step).round(decimals=2)
	l.set_fine(100)
else:
	fts = arange(args.start, args.stop, args.step).round(decimals=2)
	l.set_fine(-100)

l.set_fine(fts[0])
sleep(.1)

avgs = zeros_like(fts)
stds = zeros_like(fts)

# save data
if args.save:
	fname = datetime.now().strftime("%y.%m.%d_%H%M%S_") + args.fname+".txt"
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
  #  sleep(2)
    t = time()-stt
    l.set_fine(f)
    if d is not None:
        trans1 = d.read()
    else:
        trans1 = [0]
    acquire(fmt % i)

#    tt = concatenate((trans1, trans2))
    trans[i] = mean(trans1)
    #print trans[i]
    if args.save:
		file.write("%d\t%.3f\t%e\t%e\n" % (i, f, trans[i], std(trans1)))
if args.save:
	file.close()

# plot results
if args.plot:
    print("plotting...")
    from matplotlib.pyplot import *
    f = figure()
    plot(fts, trans, 'r.')
    xlabel("Fine Tuning Value")
    ylabel("Transmission (V)")
    show(block=True)

