#
# laserscandatas.py
#
# Successor to piezoscandatas.py
#
# Use to acquire photodiode spectrums with a Resolved Instruments DPD80 photodetector
# while stepping a Santec tunable laser over a wavelength range,=
#



import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


from time import sleep
from datetime import datetime

# use argparse module to read commandline options
import argparse

pars = argparse.ArgumentParser(description="""
""")

pars.add_argument("start", type=float, help="initial wavelength of scan")
pars.add_argument("stop", type=float, help="final wavelength of scan")
pars.add_argument("step", type=str, help="wavelength step (prefix with 'n' for number of points instead)")
pars.add_argument("-P", "--noplot", action='store_true', help="disable waiting for plot to be manually closed")

pars.add_argument("--ri-navg", type=int, default=10, 
    help="save spectrum data with ripy. uses this many ft averages")
pars.add_argument("--ri-rbw", type=float, default=100, 
    help="when saving spectrum data with ripy configures RBW (default: 100 Hz)")


args = pars.parse_args()

#
#

def get_tstamp():
    datetime.now().strftime("%Y-%m-%d_%H%M%S")

#
# calculate wavelengths
#

wls = []
if args.step[0].lower() == 'n':
    n = int(args.step[1:])
    wls = np.linspace(args.start, args.stop, n)
else:
    step = float(args.step)
    wls = np.arange(args.start, args.stop + step/2., step)

wls = wls.round(5)
trans = np.zeros_like(wls, dtype=float)

print(f"stepping: {wls}")




#
# Set up RI device
#

import ripy
from ripy_utils import spectrum
ridev = ripy.Device()
print(f"Connected to {ridev}")




#
# create plot UI
#

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), tight_layout=True)
line1 = ax1.plot(wls[:1], trans[:1], 'o-')[0]
ax1.set_xlim(wls[0], wls[-1])
ax1.set_ylim(0, 4)
ax1.set_ylabel("DC Power (W)")
ax1.set_xlabel("Wavelength (nm)")

line2 = ax2.plot([0], [1])[0]
ax2.set_yscale('log')
ax2.set_ylabel("PSD (W Hz$^{-1/2}$)")
ax2.set_xlabel("Frequency (MHz)")
fig.show()





for i, wl in enumerate(wls):
    print(f"{i:>3}: {wl}")

    # set wavelength
    # TODO

    # take ri data
    fs, Z2 = spectrum.take_spectrum(ridev, args.ri_navg, args.ri_rbw, threads=4)
    # fname = "%s_pzscan_rispectrum_navg%d_i%03d_Z" % (TSTAMP, args.ri_navg, i)
    # save(fname, Z)
    
    Z = Z2**0.5 * 1e-6 # W/rtHz

    # update plot
    trans[i] = Z[0]
    line1.set_xdata(wls[:i + 1])
    line1.set_ydata(trans[:i + 1])

    ax1.set_ylim(np.amin(trans[: i + 1]), np.amax(trans[: i + 1]))


    line2.set_xdata(fs[1:-1] * 1e-6)
    line2.set_ydata(Z[1:-1])
    ax2.set_ylim(np.amin(Z[1:-1]), np.amax(Z[1:-1]))
    ax2.set_xlim(fs[0] * 1e-6, fs[-1] * 1e-6)


    fig.canvas.draw()
    fig.canvas.flush_events()

    sleep(.1)


if not args.noplot:
    print("please close plot window to quit")
    plt.show(block=True)
