
import pyvisa
import time

#
# commande line arguments
#

import argparse

pars = argparse.ArgumentParser(description="""
sweep temperature with TED4015 controller and take course scan sweeps at each step.
""")

pars.add_argument("temp", type=str, help="temperature to set to")
pars.add_argument("--wait", action='store_true', default=False, help="wait for temperature to set")

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
    n = 0 if wait else Nmeas
    
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


setT(float(args.temp), wait=args.wait)