import midifile
from midi import *
mf = midifile.MidiFile()
parser = midifile.ParseMidi(mf)
stream = MidiInFile.MidiInFile(parser, open('0848-01.mid'))
stream.read()
mf.export('dupe.mid')

