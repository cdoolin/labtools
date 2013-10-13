from numpy import *
from numpy.fft import fft, fftshift, fftfreq

import sys

# use argparse module to read commandline options
import argparse

pars = argparse.ArgumentParser(description="""
scans laser wavelength by setting piezo voltage. 
communicates through lasernet so the lasernet server must be running. 
reads volt (transmission) from channel /Dev1/ai2 of a ni daq card.
""")

pars.add_argument("file", type=str, help="file to FT")
pars.add_argument("-f", "--ftsize", type=int, default=1024, help="fourier transform size")


args = pars.parse_args()


#  SETTINGS!

FIN = args.file
print("FTing %s" % FIN)

FOUT = FIN[:-4] + "_FTd"

with open(FIN) as f:
    topline = f.readline()
split = topline.split()

F0 = float(split[1])
RATE = float(split[3])
FTSIZE = args.ftsize
print("f0 is %f MHz\nrate is %f sps\nftsize is %d" % (F0 / 1e6, RATE, FTSIZE))


# GOTIME

print("loading...")
zidata = loadtxt(FIN, delimiter="\t")

if zidata.shape[1] > 2:
    zids = unique(zidata[:,2])
else:
    zids = [0,]
N = len(zids)

NAVG = zidata.shape[0] / N / FTSIZE
print("N: %d, NAVG: %d" % (N, NAVG))

Svs = zeros((N, FTSIZE))
tdata = zidata[:,0] + 1j*zidata[:,1]

print("FTing...")

for i in range(N):
    Sv = zeros(FTSIZE)
    for j in range(NAVG):
        ft = fft(tdata[i*NAVG*FTSIZE + j*FTSIZE:i*NAVG*FTSIZE + (j+1)*FTSIZE])
        Sv += real(ft*conjugate(ft))

    Sv /= RATE*FTSIZE*NAVG
    Sv = sqrt(Sv)
    Svs[i,:] = fftshift(Sv)

fs = fftshift(fftfreq(FTSIZE, 1/RATE)) + F0

print("saving...")
f = "%s_Sv.txt" % FOUT

if len(zids) > 1:
    savetxt(f, Svs)
else: # for igor
    savetxt(f, Svs.T, delimiter="\t", newline="\n")  
print(f)
if len(zids) > 1:
    f = "%s_ids.txt" % FOUT
    savetxt(f, zids)
    print(f)
f = "%s_fs.txt" % FOUT
if len(zids) > 1:
    savetxt(f, fs)
else: # for igor
    savetxt(f, fs.T, delimiter="\t", newline="\n")
print(f)

print("done!")
