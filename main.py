
import wave, sys, math, time

import pyaudio



# Vocalizations to be played. First number is index of sound, second is duration in frames.
# Third is how many frames are skipped. Changes the pitch. 1 is same pitch as recording
queue = []




class PieSynth():
    def __init__(self):
        self.sample_rate = 16000 #wf.getframerate()
        self.default_freq = self.noteToFrequency(57) # Recordings are in F

        self.vocal_samples = ["a0", "a1", "e0", "i0", "i1", "o0", "s", "l", "r", "n", "b", "k", "p", "f", "t", "z", "v", "m", "f", "h"]
        self.vocal_sample_data = []

        
        self.do_not_repeat = []
        for s in ["b", "k", "p", "f", "t"]:
            self.do_not_repeat.append(self.vocal_samples.index(s))

        self.do_not_pitch = []
        for s in ["s", "b", "k", "p", "f", "t", "f", "h"]:
            self.do_not_pitch.append(self.vocal_samples.index(s))

        # Import vocal sounds and load them into vocal_sample_data
        for v in self.vocal_samples:
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

                self.vocal_sample_data.append(data)


        self.pyaud = pyaudio.PyAudio()
        self.stream = self.pyaud.open(format=self.pyaud.get_format_from_width(wf.getsampwidth()),
                        channels=1,
                        rate=self.sample_rate,
                        output=True)


    # MIDI note number to frequency
    def noteToFrequency(self, midi_number):
        # Formula from wikipedia https://en.wikipedia.org/wiki/Piano_key_frequencies
        return ((2**(1/12))**(midi_number-49)) * 440

    def noteToPitch(self, midi_number):
        return (self.noteToFrequency(midi_number) / self.default_freq)


    def textToSequence(self, text, pitch=60):
        frames_per_sound = 20

        replace = {
            "a":"a0",
            "u":"a1",
            "o":"o0",
            "i":"i0",
            "e":"e0"
        }

        words = text.split()
        for word in words:
            sequence = []
            for l in word:
                sound = l

                if (sound in replace):
                    sound = replace[sound]

                sequence.append([self.vocal_samples.index(sound), frames_per_sound, pitch])
            
            self.play(sequence)
            time.sleep(.1)


    def play(self, sequence):
        for sound_index, duration, note in sequence:
            sound_length = len(self.vocal_sample_data[sound_index])
            total_frames_played = 0
            frame_playing = 0

            pitch = self.noteToPitch(note)

            # Adjusted pitch and adjusted duration override the original values

            # Certain sounds like fricatives or plosives should not be pitched
            if sound_index in self.do_not_pitch:
                adjusted_pitch = 1
            else:
                adjusted_pitch = pitch

            # Certain other sounds like plosives should not be repeated
            if sound_index in self.do_not_repeat:
                adjusted_duration = sound_length
            else:
                # For sounds that are repeated, pitch speeds up the playback, so duration is adjusted
                adjusted_duration = duration*100
            

            while True:
                if sound_length <= frame_playing: # Replay sound
                    frame_playing = 0

                if adjusted_duration < total_frames_played: # Cut off if duration is met
                    break

                frame = self.vocal_sample_data[sound_index][math.floor(frame_playing)]
                self.stream.write(frame)
                total_frames_played += 1

                # Normal pitch is 1, so it will play every frame in that case
                # The frame_n is rounded when getting the frame, so a slightly higher number 
                # like 1.1 will make it skip every tenth frame, increasing the pitch.
                frame_playing += adjusted_pitch

    
    def close(self):
        self.stream.close()
        self.pyaud.terminate()




if __name__ == "__main__":
    ps = PieSynth()
    #ps.play(queue)
    ps.textToSequence("haha hello")
    ps.close()