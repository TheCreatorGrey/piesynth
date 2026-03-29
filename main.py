
import pyaudio, wave, sys, math, time, json, re, sys



class PieSynth():
    def __init__(self):
        self.sample_rate = 16000 #wf.getframerate()
        self.default_freq = self.noteToFrequency(57) # Recordings are in F

        self.vocal_samples = ["aw", "ah", "ee", "eh", "ih", "ou", "oo", "uh", "s", "l", "r", "n", "b", "k", "p", "f", "t", "d", "z", "v", "m", "f", "h", "zh", "g", "th", "sh"]
        self.vocal_sample_data = []
        
        self.do_not_repeat = []
        for s in ["b", "k", "p", "t", "d", "g"]:
            self.do_not_repeat.append(self.vocal_samples.index(s))

        self.do_not_pitch = []
        for s in ["s", "b", "k", "p", "f", "t", "f", "h", "d", "g", "th", "sh"]:
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


        self.pronunciation_table = {}


    # MIDI note number to frequency
    def noteToFrequency(self, midi_number):
        # Formula from wikipedia https://en.wikipedia.org/wiki/Piano_key_frequencies
        return ((2**(1/12))**(midi_number-49)) * 440

    def noteToPitch(self, midi_number):
        return (self.noteToFrequency(midi_number) / self.default_freq)


    # Loads a pronunciation set from a JSON file
    def loadPronunciation(self, location):
        with open(location, "r") as file:
            pset = json.loads(file.read())

            for word in pset:
                self.pronunciation_table[word] = pset[word]

    # Gets word pronunciation from loaded pronunciation set(s) or guesses pronunciation
    def getPronunciation(self, word):
        if word in self.pronunciation_table:
            return self.pronunciation_table[word]
        else:
            # Otherwise guess

            pronunciation = []

            replace = {
                "a":"aw",
                "u":"uh",
                "o":"ou",
                "i":"ih",
                "e":"eh",
                "y":"ee",
                "c":"k",
                "w":"oo",
                "x":"k,s",

                "0":"z,ee,r,uh,oo",
                "1":"oo,uh,n",
                "2":"t,oo",
                "3":"th,r,ee",
                "4":"f,ou,r",
                "5":"f,aw,ee,v",
                "6":"s,ih,k,s",
                "7":"s,eh,v,ih,n",
                "8":"eh,ee,t",
                "9":"n,aw,ee,n"
            }

            for char in word:

                if (char in replace):
                    sound = replace[char]
                    for sound in replace[char].split(","):
                        pronunciation.append(sound) 
                else:
                    pronunciation.append(char)

            return pronunciation

    # Converts a sentence to a vocal sequence and plays it
    def speak(self, text, speed=20, pitch=57, word_delay=.06, sentence_delay=.2):

        cleaned = re.sub("[-_()/:]", " ", text.lower()) # Symbols to replace with spaces or small delays
        #cleaned = re.sub("[]", "", cleaned) # Symbols to ignore entirely
        sentences = re.split("[.!?,]", cleaned)
        for sentence in sentences:
            words = sentence.split()
            for word in words:
                pronunciation = self.getPronunciation(word)
                sequence = []
                for sound in pronunciation:
                    sequence.append([self.vocal_samples.index(sound), speed, pitch])
                
                self.play(sequence)
                time.sleep(word_delay)

            time.sleep(sentence_delay)

    def speakFromFile(self, location):
        with open(location, "r") as file:
            self.speak(file.read())


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

    #ps.loadPronunciation("pronunciation sets/enus_basic.json")
    #ps.loadPronunciation("pronunciation sets/enus_internet.json")
    ps.loadPronunciation("pronunciation sets/cmu_dict.json")

    if 1 < len(sys.argv):
        ps.speak(sys.argv[1])
    else:
        ps.speak("Welcome to Pie Synth. This is a basic speech synthesizer which uses pre-recorded samples of my voice to create speech.")

    ps.close()