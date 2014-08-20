#!/usr/bin/env python
from numpy import *

#import labdrivers
from time import sleep, time
from datetime import datetime


# use argparse module to read commandline options
import argparse

pars = argparse.ArgumentParser(description="""
steps attocube offset voltages while taking a finetuning scan with santec laser
at each offset voltage.
""")

pars.add_argument("off_start", type=float, help="start offset voltage")
pars.add_argument("off_stop", type=float, help="stop offset voltage")
pars.add_argument("off_step", type=float, help="offset voltage step")

pars.add_argument("ft_start", type=float, help="start fine tuning")
pars.add_argument("ft_stop", type=float, help="stop fine tuning")
pars.add_argument("ft_step", type=float, help="fine tuning step")

pars.add_argument("-a", "--axis", type=int, default=1,
    help="attocube axis to use (default: 1)")

pars.add_argument("-s", "--server", type=str, default="127.0.0.1",
    help="location of scantech or lasernet server (default: localhost)")
pars.add_argument("-t", "--type", type=str, default="scantech", help="either 'scantech' (default) or 'lasernet'")
pars.add_argument("-c", "--channel", type=str, default="/dev1/ai0",
    help="nidaqmx channel, when using bash on windows escape first / with // (default: /dev1/ai0)")
pars.add_argument("-p", "--port", type=str, default="COM6",
    help="com port of attocube (default: COM6)")


pars.add_argument("-v", "--volt", type=float, default=10., help="volt range for NI DAQ (default: 10 V)")
pars.add_argument("-f", "--fname", type=str, default="finescan")

args = pars.parse_args()


# initialize drivers
# scantech client (through websockets)
if args.type in ['scantech', 'st', 's']:
    from labdrivers.websocks import ScantechClient
    laser = ScantechClient(server=args.laser)

    def set_ft(ft):
        laser.set_fine(ft)

elif args.type in ['lasernet', 'ln', 'l']
    from labdrivers.websocks import LaserClient
    laser = LaserClient(server=args.laser)

    def set_ft(ft):
        laser.set_volt(ft)
else:
    print("invalid laser type specified")
    import sys
    sys.exit(1)


# nidaq
from labdrivers.daq import SimpleDaq
daq = SimpleDaq(args.channel, 10000, 20, maxv=args.volt)

# attocube
from labdrivers.attocube import Attocube
atto = Attocube(port=args.port)


# fine tunings.  santec laser has set precision of 1 pm (0.01 fine tunings)
fts = arange(args.ft_start, args.ft_stop, args.ft_step).round(decimals=2)
# offets
offs = arange(args.off_start, args.off_stop, args.off_step)


avgs = zeros((len(offs), len(fts)))
stds = zeros_like(avgs)

print("scanning... (control-c to stop)")

for i, offset in enumerate(offs):
	print("%f V" % offset)
	laser.set_fine(fts[0])
	atto.set_offset(args.axis, offset)
	sleep(.1)

	for j, ft in enumerate(fts):
		laser.set_fine(ft)
		sleep(.01)

		trans = daq.read()

		avgs[i, j] = mean(trans)
		stds[i, j] = std(trans)
print("finished")


timestamp = datetime.now().strftime("%y.%m.%d_%H%M%S_") + args.fname
print("saving to %s" % timestamp)
save(timestamp + "_trans", avgs)
save(timestamp + "_stds", stds)
save(timestamp + "_offs", offs)
save(timestamp + "_fts", fts)
