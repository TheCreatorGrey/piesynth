import numpy as np
import scipy as sy
import scipy.fftpack as syfp
import pylab as pyl
import wave

dt = 0.02071 
t = dt*np.arange(100000)             ## time at the same spacing of your data

u = []
with wave.open(f"samples/a0.wav", 'rb') as wf:
    #print(wf.readframes(8))
    #print(wf.getframerate())

    for i in range(512):
        u.append(int.from_bytes(wf.readframes(1)))

# Do FFT analysis of array
FFT = sy.fft(u)

# Getting the related frequencies
freqs = syfp.fftfreq(len(u), dt)     ## added dt, so x-axis is in meaningful units

# Create subplot windows and show plot
pyl.subplot(211)
pyl.plot(t, u)
pyl.xlabel('Time')
pyl.ylabel('Amplitude')
pyl.subplot(212)
pyl.plot(freqs, sy.log10(abs(FFT)), '.')  ## it's important to have the abs here
pyl.xlim(-.05, .05)                       ## zoom into see what's going on at the peak
pyl.show()