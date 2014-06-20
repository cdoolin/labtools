#!/usr/bin/env python
from numpy import *

from time import sleep, time

# use argparse module to read commandline options
import argparse
pars = argparse.ArgumentParser(description="""
Sets the fine tuning of a santech laser.
""")

pars.add_argument("ft", type=float, help="fine tuning setpoint")
pars.add_argument("-l", "--laser", type=str, default="127.0.0.1",
    help="location of scantech server")
pars.add_argument("--initial", "-i", action="store", default=None,
	help="initial finetuning to scan to setpoint from")
pars.add_argument("--num", "-n", action="store", type=int, default=50,
	help="number of setpoints when scanning in")

args = pars.parse_args()

if args.initial is not None:
	fts = linspace(float(args.initial), args.ft, num=args.num, endpoint=True)
else:
	fts = [args.ft]

# initialize drivers
# scantech client (through websockets)
from labdrivers.websocks import ScantechClient
l = ScantechClient(args.laser)

for f in fts:
	l.set_fine(round_(f, decimals=2))
