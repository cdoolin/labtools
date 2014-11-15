#!/bin/env python

import argparse

pars = argparse.ArgumentParser(description="""
scans newfocus piezo using lasernet.  takes data at piezo offsets.
""")
pars.add_argument("--laser", default="localhost", help="set lasernet address")
pars.add_argument("--slew", type=float, default=5, help="slew rate (default 5 nm/s)")
pars.add_argument("--start", type=float, default=765, help="start wavelength (default 765 nm)")
pars.add_argument("--stop", type=float, default=781, help="stop wavelength (nm)")
pars.add_argument("--text", type=str, default="repeat", help="text to add to filename (default 'repeat')")
args = pars.parse_args()

import labdrivers.websocks
laser = labdrivers.websocks.LaserClient(args.laser)

import msvcrt

GO = False

print("Press 'G' to start scanning.  'S' to stop.")

while True:
    if msvcrt.kbhit() > 0:
        c = msvcrt.getch()
        if c in ['g', 'G']:
            GO = True
        elif c in ['s', 'S']:
            GO = False
        elif c in ['q', 'Q']:
            return

    if GO:
        laser.scan(args.start, args.stop
    else:
        time.sleep(.1)
    
msvcrt.getch()
