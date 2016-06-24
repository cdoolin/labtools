



import argparse
parser = argparse.ArgumentParser(description="control voa and take megadata")

parser.add_argument("--power", default=5, type=float, help="On voltage of VOA")
parser.add_argument("--delay", default=10, type=float, help="Delay between starting megadaq and turning on voa (in ms)")
parser.add_argument("pulselength", type=float, help="length of laser pulse (in ms)")
parser.add_argument("--pause", default=0.5, type=float, help="delay between pulses (and time to let megadata get ready). if 0 only arms megadata once not between scans.")
parser.add_argument("--scans", default=0, type=int, help="number of scans  to take (0 -> unlimited)")

parser.add_argument("-d", "--device", default="dev1", help="NIDAQ device name (default: Dev1)")
parser.add_argument("--megadaq", default="aerodaqtyl", help="getdata server address")
parser.add_argument("--rate", default=1000., type=float, help="sample rate to write volteges at (sps)")
parser.add_argument("--onetrigger", default=False, action="store_true", help="sample rate to write volteges at (sps)")

args = parser.parse_args()


#
#  Set up megadata drivers
#

import zmq

context = zmq.Context()
s = context.socket(zmq.REQ)
server = "tcp://%s:6497" % args.megadaq
s.connect(server)
print("connected to %s" % server)

def megasave(desc):
    s.send("startacquire;%s" % desc)
    s.recv()
    

#
#  Set up nidaqmx stuff
#
#  Analog out 0 - controls mems voa
#  Analog out 1 - generate 3.3 V for triggering aerodaqtyl
#

import numpy as np
from labdrivers import nidaqmx

RATE = args.rate

state_ready = np.r_[5., 3.3]
state_trigger_daq = np.r_[5., 0]
state_trigger_voa = np.r_[args.power, 3.3]
state_pulse = np.r_[args.power, 0]


n_trigger = abs(int(args.delay * 0.001 * RATE))
if n_trigger < 1:
    n_trigger = 0
n_pulse = int(args.pulselength * 0.001 * RATE)

if args.delay >= 0: # trigger voa after daq
    state_trigger = state_trigger_daq
else: # trigger daq after voa
    state_trigger = state_trigger_voa

waveform = np.r_[
    state_ready,
    np.tile(state_trigger, n_trigger),
    np.tile(state_pulse, n_pulse),
    state_ready
]

analog_task = nidaqmx.AnalogOutputTask()
analog_task.create_voltage_channel("/%s/ao0:1" % args.device, min_val=0, max_val=5)
analog_task.configure_timing_sample_clock(rate=RATE, samples_per_channel=len(waveform)/2, sample_mode="finite")

analog_task.write(waveform, timeout=10, auto_start=False)

print("delay after trigger: %.2f ms" % (n_trigger / RATE * 1000))
print("pulse duration: %.2f ms" % (n_pulse / RATE * 1000))

print("est. blocks needed: %.2f" % (5e8 * n_pulse / RATE / 2**19))


import msvcrt
import time
import sys
out = sys.stdout

go = True
i = 1

print("starting data collection.  press 'q' to stop")

if args.onetrigger:
    megasave("%g_pause_%.2f_power_%d_scans" % (args.pause, args.power, args.scans))
    time.sleep(2)

while go:
    out.write("scan %d..." % i)
    if not args.onetrigger:
        megasave("%05d" % i)
        time.sleep(args.pause)
        out.write("  ok. pulsing...")
    else:
        time.sleep(args.pause)
        
    analog_task.start()
    analog_task.wait_until_done()
    analog_task.stop()
    out.write(" done.\r\n")
    
    i += 1
    
    if args.scans > 0 and i > args.scans:
        go = False
    
    while msvcrt.kbhit() > 0:
        c = msvcrt.getch()
        if c == 'p':
            print("paused..")
            msvcrt.getch()
            print("resumed")
        elif c == 'a':
            print('a pressed')
        elif c == 'q':
            print("stopping..")
            go = False
            break
            
    
    
# while msvcrt.kbhit() < 1:
#    scan_and_save()

#msvcrt.getch()

#analog_task.write([volt, volt])
