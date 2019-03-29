
#
# pulsed-ringdown.py
#

desc = """
generates double-pulse sequence to measure ringdown of mechanical devices
as they heat up and ring down from optical measurements.
"""

import datetime
import numpy
import argparse

pars = argparse.ArgumentParser(description=desc)


pars.add_argument("ringdowns", type=str,
    help="comma seperated list of ringdown times")


pars.add_argument("--test", action='store_true', default=False,
    help="run in test mode without taking data")

pars.add_argument("--t-heat", type=str, default="20m",
    help="time to heat device for (default: 20m)")
# pars.add_argument("--t-ring", type=str, default="5m",
#     help="time to heat device for")
pars.add_argument("--t-meas", type=str, default="10m",
    help="time to measure device for (default: 10m)")
pars.add_argument("--t-pretrig", type=str, default="5m",
    help="time before measurement to trigger data collection (default: 5m)")
pars.add_argument("--pavg", type=float, default=0.1,
    help="average on-time of pulse train (default: 0.1)")

pars.add_argument("--npulses", type=int, default=1000, 
    help="number of pulses to capture for each ringdown time (default: 1000)")


pars.add_argument("--channel-aom", type=str, default="dev2/ao0", 
    help="analog nidaq channel to generate aom control sequence on")
pars.add_argument("--channel-trig", type=str, default="dev2/ao1", 
    help="analog nidaq channel to generate trigger control sequence on")

pars.add_argument("--drive-rate", type=float, default=800e3,
    help="samplerate to generate control signal at (default: 800e3)")


args = pars.parse_args()


def parse_time(s):
    s = s.replace("m", "e-3")
    s = s.replace("u", "e-6")
    return float(s)

Theat = parse_time(args.t_heat)
Tmeas = parse_time(args.t_meas)
Tpretrig = parse_time(args.t_pretrig)
Ttrigon = 1e-3

#
#  parse ringdown times
#

def parse_ringdowns(s):
    try:
        with open(s, 'r') as f:
            txt = f.read()
        print("loaded ringdowns from '{s}'")
    except FileNotFoundError:
        txt = s

    txt = txt.replace(',', ' ')
    txt = txt.replace("m", "e-3")
    txt = txt.replace("u", "e-6")

    rtimes = [float(ss) for ss in txt.split()]
    return rtimes


ringdowns = parse_ringdowns(args.ringdowns)
ringdowns_s = ', '.join(["%g" % r for r in ringdowns])
print(f"ringdown times: {ringdowns_s}")

#
#
#



#
# create and configure task for control waveform output
#

Noutsamps = int((Theat + Tmeas) / args.pavg * args.drive_rate)

import nidaqmx

outtask = nidaqmx.Task()

outtask.ao_channels.add_ao_voltage_chan(
    f"/{args.channel_aom},{args.channel_trig}", 
    min_val=0, max_val=5)

outtask.timing.cfg_samp_clk_timing(
    rate=args.drive_rate, 
    samps_per_chan=Noutsamps,
    sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)



def generate_control_sig(
        Tring, Theat=Theat, Tmeas=Tmeas, Pavg=args.pavg,
        Tpretrig=Tpretrig, Ttrigon=1e-3, rate=args.drive_rate):
    ON = [3.3]
    OFF = [0]

    Tcool = (Theat + Tmeas) / Pavg - Tring - Theat - Tmeas
    if Tcool < 0:
        Tcool = 0

    wave_aom = [
        OFF * int(Tcool * rate + 0.5),
        ON * int(Theat * rate + 0.5),
        OFF * int(Tring * rate + 0.5),
        ON * int(Tmeas * rate + 0.5),
    ]
    wave_aom = numpy.hstack(wave_aom)

    wave_trig = [
        OFF * int((Tcool + Theat + Tring - Tpretrig) * rate  + 0.5),
        ON * int(Ttrigon * rate  + 0.5),
        OFF * int((Tmeas + Tpretrig - Ttrigon) * rate  + 0.5),
    ]
    wave_trig = numpy.hstack(wave_trig)

    return wave_aom, wave_trig


#
# create ripy Device for data capture
#

import ripy
import tqdm

ridev = ripy.Device()

def capture_pulses(npulses, ncaps=100, Tcap=Tpretrig + Tmeas, dev=ridev):
    """
    breaks capture into multiple get_raw_data calls to 
    enable reporting of capture status with tqdm
    """

    Npulsepercap = npulses // ncaps
    Nsampperpulse = int(Tcap * dev.samplerate)

    alldata = []
    for i in tqdm.tqdm(range(ncaps)):
        data = dev.get_raw_data(
            Nsampperpulse*Npulsepercap, 
            mask=False, 
            trig_mode='rising', trig_port='T',
            samples_per_trigger=Nsampperpulse,
            arm_time=100)
        alldata.append(data)

    dd = numpy.hstack(alldata)
    return dd.reshape((len(dd)//Nsampperpulse, Nsampperpulse))
    


#
# main loop
#

# if __name__ == '__main__':

for ringdown in ringdowns:
    print(f"ringdown {ringdown}")

    wave_aom, wave_trig = generate_control_sig(ringdown)
    # assert len(wave_aom) == Noutsamps
    # assert len(wave_trig) == Noutsamps
    outtask.timing.cfg_samp_clk_timing(
        rate=args.drive_rate, 
        samps_per_chan=len(wave_aom),
        sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
    outtask.write([list(wave_aom), list(wave_trig)], timeout=10, auto_start=False)

    t0 = datetime.datetime.now()

    outtask.start()
    if not args.test:
        data = capture_pulses(args.npulses)
    outtask.stop()

    t1 = datetime.datetime.now()
    dt = (t1 - t0).seconds
    tstamp = t0.strftime("%y.%m.%d_%H%M%S")

    fname = f"{tstamp}_dt{dt}_npulses{args.npulses}_ringdown{'%e' % ringdown}.npy"
    print(f"saving to {fname}")

    if not args.test:
        numpy.save(fname, data)


outtask.__exit__(None, None, None)


