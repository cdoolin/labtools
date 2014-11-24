#!/bin/env python

import argparse

pars = argparse.ArgumentParser(description="""
scans newfocus piezo using lasernet.  takes data at piezo offsets.
""")
pars.add_argument("--laser", default="localhost", help="set lasernet address")
pars.add_argument("--slew", type=float, default=5, help="slew rate (default 5 nm/s)")
pars.add_argument("--start", type=float, default=765, help="start wavelength (default 765 nm)")
pars.add_argument("--stop", type=float, default=781, help="stop wavelength (nm)")
pars.add_argument("--text", type=str, default="scan", help="text to add to filename (default 'repeat')")
args = pars.parse_args()

import labdrivers.websocks
laser = labdrivers.websocks.LaserClient(args.laser)

import msvcrt
import time

SCAN = False
GO = True

print("Press 'g' to start scanning. 's' to stop. 'q' to quit.")

i = 0

while GO:
    while msvcrt.kbhit() > 0:
        c = msvcrt.getch()
        if c is 'a':
            print("pressed a")
        if c in ['g', 'G']:
            print("scanning...")
            SCAN = True
        elif c in ['s', 'S']:
            print("stopped.")
            SCAN = False
        elif c in ['q', 'Q']:
            GO = SCAN = False

    if SCAN:
        print(i)
        laser.scan(args.start, args.stop, args.slew, "%s%04d" % (args.text, i))
        i += 1
    else:
        time.sleep(.05)
    
#msvcrt.getch()
