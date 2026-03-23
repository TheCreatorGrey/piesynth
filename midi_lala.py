from main import PieSynth
import mido

ps = PieSynth()
##ps.play(queue)


tracks = [[], [], [], []]
mid = mido.MidiFile('megalovania.mid')
notes_playing = 0
for msg in mid.play():
    if notes_playing == 0:
        if msg.type == "note_on":
            print(msg.note)

            ps.play([[0, 20, msg.note]])

    if msg.type == "note_on":
        notes_playing += 1
    
    if msg.type == "note_off":
        notes_playing -= 1

ps.close()