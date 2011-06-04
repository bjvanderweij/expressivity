from MidiRepresentation import *
from music21 import converter

align(score, performance):
  

if __name__ == "__main__":
  roll = PianoRoll('0848-01.mid')
  score = converter.parse('0848-01.mid')
  align(score, roll)
