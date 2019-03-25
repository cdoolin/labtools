# import pyvisa
import serial
import datetime
import time
import msvcrt

import argparse

parser = argparse.ArgumentParser(description='Measure rtd resistance with laser-controller board.')
parser.add_argument("--port", type=str, default="COM5",
                    help='serial port to use (default: COM5')
parser.add_argument('--rtd', type=int, default=1,
                    help='which RTD to measure (default: 1)')

args = parser.parse_args()


RREF = 2000 # kOhms

ser = serial.Serial(args.port, 9600, timeout=1)

ser.write(b"echo 0\r\n")
ser.readline()

def get_resistance():
    ser.write(b"get_rtd %d\r\n" % args.rtd)
    return float(ser.readline().decode().strip()) / 1000.

def get_dt():
    return datetime.datetime.now().strftime("%y.%m.%d_%H%M%S")


fname = "%s_lasercontroller_log.txt" % get_dt()
f = open(fname, 'w')
print("opened %s" % fname)


print("Press 'g' to start scanning. 's' to stop. 'q' to quit.")


GO = True
SCAN = False
while GO:
    while msvcrt.kbhit() > 0:
        c = msvcrt.getch().decode()
        if c in ['g', 'G']:
            print("scanning...")
            SCAN = True
        elif c in ['s', 'S']:
            print("stopped.")
            SCAN = False
        elif c in ['q', 'Q']:
            GO = SCAN = False
        else:
            print("pressed %s" % c)

    if SCAN:
        msg = "%s  %f" % (get_dt(), get_resistance())
        f.write(msg + "\n")
        f.flush()
        print(msg)
        time.sleep(1)

    else:
        time.sleep(.05)

ser.close()
f.close()
