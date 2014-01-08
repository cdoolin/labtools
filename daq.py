from libnidaqmx import AnalogInputTask
#import numpy as np

class SimpleReader(object):
    def __init__(self, channels, rate, n,maxv=3.):
        self.n = n
        
        self.task = AnalogInputTask()

        if isinstance(channels, str):
            channels = [channels]
        for c in channels:
            self.task.create_voltage_channel(
                channel, terminal = 'diff',
                min_val=-maxv, max_val=maxv)

        self.task.configure_timing_sample_clock(
            rate=rate, sample_mode='finite', samples_per_channel=n)

    def read(self):
        self.task.start()
        data = self.task.read(self.n, fill_mode='group_by_channel')
        self.task.stop()
        return data[0]
