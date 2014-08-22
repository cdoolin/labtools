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
laser = LaserClient(server=args.server)

# attocube
from labdrivers.attocube import Attocube
atto = Attocube(port=args.port)


def stepto(a, b, d):
    d = abs(d) if b > a else -abs(d)
    yield a
    while abs(b - a) > abs(d):
        a += d
        yield a
    yield b

# offets
#offs = arange(args.off_start, args.off_stop, args.off_step)
#if any(offs - floor(offs) > 0):
#    yn = raw_input("volt offsets truncated in filename. continue? [y/N]")
#    if yn != "y":
#        import sys
#        sys.exit(0)

# calculate number of digits to use when saving
#digits = ceil(log10(max(abs(offs)) + .001))

#from  math import log10, floor, ceil
#decimals = -floor(log10(args.off_step))
digits = ceil(log10(max(abs(args.off_start), abs(args.off_stop)) +.001))
#if decimals <= 0:
#    fmtstr = "%%0%d.0fV" % digits
#else:
#    fmtstr = "%%0%d.%dfV" % (decimals + digits + 1, decimals)
#
#try:
#    decimals = len(str(args.off_step).split('.')[1])
#except ValueError:
#    decimals = 0


print("scanning... (control-c to stop)")

for offset in stepto(args.off_start, args.off_stop, args.off_step):
    print("%g V" % offset)
    #laser.set_fine(fts[0])
    atto.slideto(args.axis, offset)
    sleep(.1)

    text = "%gV" % offset
    try:
        dec = text.index('.')
    except ValueError:
        dec = len(text) - 1
    if dec < digits:
        text = "0" * (digits - dec) + text

    laser.scan(args.wl_start, args.wl_stop, args.wl_slew, save=text)
    
print("finished")

