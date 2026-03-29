import requests, json

# This script fetches and converts the CMU Pronounciation Dictionary to a pronounciation table compatible with PieSynth

'''
        Phoneme Example Translation
        ------- ------- -----------
        AA	odd     AA D
        AE	at	AE T
        AH	hut	HH AH T
        AO	ought	AO T
        AW	cow	K AW
        AY	hide	HH AY D
        B 	be	B IY
        CH	cheese	CH IY Z
        D 	dee	D IY
        DH	thee	DH IY
        EH	Ed	EH D
        ER	hurt	HH ER T
        EY	ate	EY T
        F 	fee	F IY
        G 	green	G R IY N
        HH	he	HH IY
        IH	it	IH T
        IY	eat	IY T
        JH	gee	JH IY
        K 	key	K IY
        L 	lee	L IY
        M 	me	M IY
        N 	knee	N IY
        NG	ping	P IH NG
        OW	oat	OW T
        OY	toy	T OY
        P 	pee	P IY
        R 	read	R IY D
        S 	sea	S IY
        SH	she	SH IY
        T 	tea	T IY
        TH	theta	TH EY T AH
        UH	hood	HH UH D
        UW	two	T UW
        V 	vee	V IY
        W 	we	W IY
        Y 	yield	Y IY L D
        Z 	zee	Z IY
        ZH	seizure	S IY ZH ER
'''

# The CMU dict uses the ARPAbet for pronunciation.
arpa_to_pie = {
    "AA":"aw",
    "AE":"ah",
    "AH":"uh",
    "AO":"ou",
    "AW":"ah,oo",
    "AY":"aw,ee",
    "CH":"t,sh",
    "DH":"th", # Needs to be voiced
    "EH":"eh", # redundant definition for match
    "ER":"r",
    "EY":"eh,ee", # May need adjustment
    "HH":"h",
    "IH":"ih",
    "IY":"ee",
    "JH":"d,zh",
    "NG":"n", # An actual ng sound needs to be added
    "OW":"uh,oo",
    "OY":"ou,ee",
    "UH":"uh", # Needs w[oo]d sound
    "UW":"oo",
    "W":"oo",
    "Y":"ee"
}

#with open("sphinx.txt") as file:
#    raw = file.read()


print("Fetching dataset...")
response = requests.get("https://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/sphinxdict/cmudict.0.7a_SPHINX_40")
raw = response.text
print("Server responded.")

pronunciation_table = {}

print("Converting dataset...")
lines = raw.split("\n")
for line in lines:
    if not line:
        continue

    word, phones_raw = line.replace("\r", "").split("\t") # Ignore \r. Words and pronunciation are separated by \t.
    phones = phones_raw.split(" ")

    pronounciation = []
    for p in phones:
        if p in arpa_to_pie:
            # Only representations for sounds that don't already match will be specified in the table
            for sound in arpa_to_pie[p].split(","):
                pronounciation.append(sound)
        else:
            pronounciation.append(p.lower())

    pronunciation_table[word.lower()] = pronounciation

    #print(word, phones, pronounciation)

print("Saving...")
with open("pronunciation sets/cmu_dict.json", "w") as file:
    file.write(json.dumps(pronunciation_table))

print("Finished.")