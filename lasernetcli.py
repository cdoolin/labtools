#!/bin/env python

# use argparse module to read commandline options
import argparse

pars = argparse.ArgumentParser(description="""
command line interface for lasernet
""")

pars.add_argument("--server", default="localhost", help="lasernet server address")
pars.add_argument("--wave", default=None, type=float, help="set wavelength")
pars.add_argument("--piezo", default=None, type=float, help="set piezo")

args = pars.parse_args()

import labdrivers.websocks
laser = labdrivers.websocks.LaserClient(args.server)

if args.wave:
    laser.set_wave(args.wave)

if args.piezo:
    laser.set_volt(args.piezo)
