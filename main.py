
import wave, sys, math

import pyaudio


CHUNK = 512
sample_rate = 16000 #wf.getframerate()

vocal_samples= ["ou", "ah", "er"]
vocal_sample_data = []

# Import vocal sounds and load them into vocal_sample_data
for v in vocal_samples:
    with wave.open(f"samples/{v}.wav", 'rb') as wf:
        #print(wf.readframes(8))
        #print(wf.getframerate())

        data = []
        for i in range(CHUNK):
            data.append(wf.readframes(1))

        vocal_sample_data.append(data)




p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=1,
                rate=sample_rate,
                output=True)

# Vocalizations to be played. First number is index of sound, second is duration in frames.
queue = [
    [2, 40],
    [1, 40],
    [2, 40],
    [1, 40],
    [0, 50],
    [1, 100]
]

# How many frames are skipped. Changes the pitch.
pitch = 1.1

for sound_index, duration in queue:
    for i in range(math.floor(duration*pitch)): # The pitch speeds up the playback, so duration is adjusted
        length = len(vocal_sample_data[sound_index])
        frame_n = 0
        while frame_n < length:
            frame = vocal_sample_data[sound_index][math.floor(frame_n)]
            stream.write(frame)

            # Normal pitch is 1, so it will play every frame in that case
            # The frame_n is rounded when getting the frame, so a slightly higher number 
            # like 1.1 will make it skip every tenth frame, increasing the pitch.
            frame_n += pitch
        pitch += 0.001



stream.close()
p.terminate()