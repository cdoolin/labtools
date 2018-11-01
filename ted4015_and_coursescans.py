import pyvisa
import datetime
import time
import msvcrt

from numpy import arange

#
# commande line arguments
#

import argparse

pars = argparse.ArgumentParser(description="""
sweep temperature with TED4015 controller and take course scan sweeps at each step.
""")

pars.add_argument("--laser", default="localhost", help="set lasernet address")
pars.add_argument("--slew", type=float, default=5, help="slew rate (default 5 nm/s)")
pars.add_argument("--start", type=float, default=765, help="start wavelength (default 765 nm)")
pars.add_argument("--stop", type=float, default=781, help="stop wavelength (nm)")
pars.add_argument("--text", type=str, default="scan", help="text to add to filename (default 'repeat')")

pars.add_argument("--nscans", type=int, default=2, help="course scans to do at each wavelength")
pars.add_argument("--tstart", type=float, default=20, help="temperature start")
pars.add_argument("--tstop", type=float, default=60, help="temperature end")
pars.add_argument("--tstep", type=float, default=5, help="temperature step")

args = pars.parse_args()


#
# initialize TED4015 communication
#

rm = pyvisa.ResourceManager()

try:
    i = rm.open_resource("USB0::0x1313::0x8048::M00324477::INSTR")
except:
    print("could not open instrument")
    import sys
    sys.exit(0)

i.write("CONF:TEMP")

def get_temp():
    i.write("CONF:TEMP")
    return float(i.query("READ?"))

def get_dt():
    return datetime.datetime.now().strftime("%y.%m.%d_%H%M%S")

def setT(T, Terr=0.05, timeout=30, wait=True, settling=3, rate=10):
    Nmeas = rate*settling
    
    T = float(T)
    i.write("SOUR:TEMP %.2fC" % T)

    time0 = time.time()
    timedout = False
    n = 0
    
    while n < Nmeas and not timedout:
        time.sleep(1./float(rate))
        i.write("CONF:TEMP")
        Tmeas = float(i.query("READ?").strip())
        
        if abs(T - Tmeas) < Terr:
            n += 1
        else:
            n = 0
            
        timedout = abs(time.time() - time0) > timeout

    if timedout:
        print("setting temp timed out")


#
# initialize lasernet
#

import labdrivers.websocks
laser = labdrivers.websocks.LaserClient(args.laser)

def do_scan(t, i):
    laser.scan(args.start, args.stop, args.slew, "%.02fC_%d" % (t, i))


# open file for saving

fname = "%s_ted4015_scan.txt" % get_dt()
f = open(fname, 'w')
print("opened %s" % fname)


# set up temperature sweep

temps = arange(args.tstart, args.tstop + args.tstep/2., args.tstep)

for t in temps:
    print(t)
    setT(t)

    for j in range(args.nscans):
        do_scan(t, j)


setT(temps[0])


i.close()
f.close()
