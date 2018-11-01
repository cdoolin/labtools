# import pyvisa
import serial
import datetime
import time
import msvcrt


# rm = pyvisa.ResourceManager()

# try:
#     i = rm.open_resource("USB0::0x1313::0x8048::M00324477::INSTR")
# except:
#     print("could not open instrument")
#     import sys
#     sys.exit(0)

# i.write("CONF:TEMP")


# def get_temp():
#     return float(i.query("READ?"))

RREF = 2000 # kOhms

ser = serial.Serial('COM3', 38400, timeout=1)


def get_resistance():
    ser.write(b"get_resistance\n")
    return float(ser.readline().decode().strip()) / float(0x8000) * RREF/2.

def get_dt():
    return datetime.datetime.now().strftime("%y.%m.%d_%H%M%S")


fname = "%s_microRTD_log.txt" % get_dt()
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
