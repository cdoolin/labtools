from numpy import *
import sys
import os

for fname in sys.argv[1:]:
    print("loading %s" % fname)
    data = loadtxt(fname)
    print("saving %s.npy" % fname[:-4])
    save(fname[:-4], data)
