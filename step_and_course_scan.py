#!/usr/bin/env python
from numpy import *

#import labdrivers
from time import sleep, time
from datetime import datetime


# use argparse module to read commandline options
import argparse

pars = argparse.ArgumentParser(description="""
steps attocube offset voltages while taking a course scan using lasernet""")

pars.add_argument("off_start", type=float, help="start offset voltage")
pars.add_argument("off_stop", type=float, help="stop offset voltage")
pars.add_argument("off_step", type=float, help="offset voltage step")

pars.add_argument("wl_start", type=float, help="start wavelength")
pars.add_argument("wl_stop", type=float, help="stop wavelength")
pars.add_argument("wl_slew", type=float, help="scan speed")

pars.add_argument("-a", "--axis", type=int, default=1,
    help="attocube axis to use (default: 1)")

pars.add_argument("-s", "--server", type=str, default="127.0.0.1",
    help="location of scantech or lasernet server (default: localhost)")
pars.add_argument("-p", "--port", type=str, default="COM6",
    help="com port of attocube (default: COM6)")


#pars.add_argument("-f", "--fname", type=str, default="finescan")

args = pars.parse_args()

# initialize drivers
from labdrivers.websocks import LaserClient
laser = LaserClient(server=args.laser)

# attocube
from labdrivers.attocube import Attocube
atto = Attocube(port=args.port)

# offets
offs = arange(args.off_start, args.off_stop, args.off_step)
if any(a - floor(a) > 0):
    yn = raw_input("volt offsets truncated in filename. continue? [y/N]")
    if yn != "y":
        import sys
        sys.exit(0)

# calculate number of digits to use when saving
digits = ceil(log10(max(abs(offs)) + .001))

print("scanning... (control-c to stop)")

for i, offset in enumerate(offs):
	print("%f V" % offset)
	#laser.set_fine(fts[0])
	atto.set_offset(args.axis, offset)
	sleep(.1)
    laser.scan(args.wl_start, args._wl_stop, args._wl_slew, save="%%0%d.0f" % digits % offset)
	
print("finished")

