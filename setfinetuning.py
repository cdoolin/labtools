#!/usr/bin/env python
from numpy import *

from time import sleep, time
from datetime import datetime

# use argparse module to read commandline options
import argparse

pars = argparse.ArgumentParser(description="""
scans wavelength with santec laser and collects megadaqtyl data 
and dc transmission (nidaq) data.
""")

pars.add_argument("finetuning", type=float, help="start wavelength")

pars.add_argument("-l", "--laser", type=str, default="127.0.0.1",
    help="location of scantech server")

pars.add_argument("-c", "--channel", type=str, default="/dev1/ai0",
    help="nidaqmx channel (default: /dev1/ai0)")
	
pars.add_argument("-m", "--mhz", action='store_true', default=False)



args = pars.parse_args()


# initialize drivers
# scantech client (through websockets)
from labdrivers.websocks import ScantechClient
l = ScantechClient(args.laser)

if args.mhz:
	args.finetuning = -1*(args.finetuning)/50 + float(l.check_ft()['ret'])

if args.finetuning == "-1000":
    print float(l.check_ft()['ret'])
else:
    l.set_fine(float(args.finetuning))
    print l.check_ft()
sleep(.1)
