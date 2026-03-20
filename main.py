
import wave, sys, math

import pyaudio


CHUNK = 4096
sample_rate = 16000 #wf.getframerate()

vocal_samples= ["a0", "a1", "e0", "i0", "i1", "o0", "l", "r", "n", "p", "f", "t"]
vocal_sample_data = []

do_not_repeat = [9, 12]
do_not_pitch = [9, 10, 11]

# Import vocal sounds and load them into vocal_sample_data
for v in vocal_samples:
    with wave.open(f"samples/{v}.wav", 'rb') as wf:
        #print(wf.readframes(8))
        #print(wf.getframerate())

        data = []
        while True:
            frame = wf.readframes(1)
            if frame:
                data.append(frame)
            else:
                break

        vocal_sample_data.append(data)




p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=1,
                rate=sample_rate,
                output=True)

# MIDI note number to frequency
def noteToFrequency(midi_number):
    # Formula from wikipedia https://en.wikipedia.org/wiki/Piano_key_frequencies
    return ((2**(1/12))**(midi_number-49)) * 440

default_freq = noteToFrequency(91) # Recordings are in F
def noteToPitch(midi_number):
    return default_freq / noteToFrequency(midi_number)

print(default_freq)
print(noteToFrequency(94))



# Vocalizations to be played. First number is index of sound, second is duration in frames.
# Third is how many frames are skipped. Changes the pitch. 1 is same pitch as recording
queue = [
    [9, 10, 1],
    [3, 10, 1],
    [9, 10, 1],
    [3, 10, 1],

    [10, 20, 1],

    [7, 10, 1],
    [4, 10, 1.1],
    [8, 10, 1.05],
    [8, 20, 1],

    [6, 10, noteToPitch(80)],
    [0, 20, noteToPitch(80)],
    [6, 10, noteToPitch(82)],
    [0, 20, noteToPitch(82)],
    [6, 10, noteToPitch(84)],
    [0, 20, noteToPitch(84)],
    [6, 10, noteToPitch(82)],
    [0, 20, noteToPitch(82)],
    [6, 10, noteToPitch(80)],
    [0, 20, noteToPitch(80)],
    [6, 10, noteToPitch(80)],
    [0, 20, noteToPitch(80)],
    [6, 10, noteToPitch(80)],
    [0, 30, noteToPitch(80)],
    [6, 10, noteToPitch(82)],
    [0, 20, noteToPitch(82)],
    [6, 10, noteToPitch(82)],
    [0, 20, noteToPitch(82)],
    [6, 10, noteToPitch(82)],
    [0, 30, noteToPitch(82)],
    [6, 10, noteToPitch(80)],
    [0, 20, noteToPitch(80)],
    [6, 10, noteToPitch(77)],
    [0, 20, noteToPitch(77)],
    [6, 10, noteToPitch(77)],
    [0, 30, noteToPitch(77)],
    [6, 10, noteToPitch(80)],
    [0, 20, noteToPitch(80)],
    [6, 10, noteToPitch(82)],
    [0, 20, noteToPitch(82)],
    [6, 10, noteToPitch(84)],
    [0, 20, noteToPitch(84)],
    [6, 10, noteToPitch(82)],
    [0, 20, noteToPitch(82)],
    [6, 10, noteToPitch(80)],
    [0, 20, noteToPitch(80)],
    [6, 10, noteToPitch(80)],
    [0, 20, noteToPitch(80)],
    [6, 10, noteToPitch(80)],
    [0, 20, noteToPitch(80)],
    [6, 10, noteToPitch(80)],
    [0, 20, noteToPitch(80)],
    [6, 10, noteToPitch(82)],
    [0, 20, noteToPitch(82)],
    [6, 10, noteToPitch(82)],
    [0, 20, noteToPitch(82)],
    [6, 10, noteToPitch(80)],
    [0, 20, noteToPitch(80)],
    [6, 10, noteToPitch(82)],
    [0, 20, noteToPitch(82)],
    [6, 10, noteToPitch(84)],
    [0, 20, noteToPitch(84)],



    [0, 80, noteToPitch(92)],
    [1, 80, noteToPitch(92)],
    [2, 80, noteToPitch(92)],
    [3, 80, noteToPitch(92)],
    [4, 80, noteToPitch(92)],
    [5, 80, noteToPitch(92)],

    [0, 40, noteToPitch(92)],
    [1, 40, noteToPitch(91)],
    [2, 40, noteToPitch(90)],
    [3, 40, noteToPitch(89)],
    [4, 40, noteToPitch(88)],
    [5, 40, noteToPitch(87)],
]

for sound_index, duration, pitch in queue:
    total_frames_played = 0
    frame_playing = 0

    sound_length = len(vocal_sample_data[sound_index])

    # Adjusted pitch and adjusted duration override the original values

    # Certain sounds like fricatives or plosives should not be pitched
    if sound_index in do_not_pitch:
        adjusted_pitch = 1
    else:
        adjusted_pitch = pitch

    # Certain other sounds like plosives should not be repeated
    if sound_index in do_not_repeat:
        adjusted_duration = sound_length
    else:
        # For sounds that are repeated, pitch speeds up the playback, so duration is adjusted
        adjusted_duration = math.floor(duration*adjusted_pitch)*100
    

    while True:
        if sound_length <= frame_playing: # Replay sound
            frame_playing = 0

        if adjusted_duration < total_frames_played: # Cut off if duration is met
            break

        frame = vocal_sample_data[sound_index][math.floor(frame_playing)]
        stream.write(frame)
        total_frames_played += 1

        # Normal pitch is 1, so it will play every frame in that case
        # The frame_n is rounded when getting the frame, so a slightly higher number 
        # like 1.1 will make it skip every tenth frame, increasing the pitch.
        frame_playing += adjusted_pitch



stream.close()
p.terminate()