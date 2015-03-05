from midi.MidiOutStream import MidiOutStream
from representation import *
import sys, math, random


def averagePitch(roll):
  pitches = []
  for note in roll:
    pitches.append(note.note)
  return sum(pitches)/len(pitches)

def higherIsFaster(roll, scale):
  print("Calculating average pitch")
  avg = averagePitch(roll)
  print("Average pitch: {0}".format(avg))
  print("Adding expression")
  bassnote = False
  for note in roll:
    pitch = note.note
    diff = pitch - avg
    speedup = -math.pow(diff/scale, 3.0) + 1.0
    if bassnote:
      bassnote = False
      speedup = lastspeedup
      note.offset -= diff
    if note.__next__:
      if note.next.note_on() == note.note_on():
        bassnote = True
    diff = int(note.length * speedup) - note.length
    note.setLength(int(note.length * speedup))
    lastspeedup = speedup

def randomNoise(roll, maxDiff):
  for note in roll.notes:
    roll.move(note, int(random.random() * maxDiff - maxDiff/2.0))



if __name__ == '__main__':
  import sys
  inp = sys.argv[1]
  roll = PianoRoll(inp)
  higherIsFaster(roll, 100.0)
  roll.exportMidi('expression_output.mid')
  randomNoise(roll, 20)
  roll.exportMidi('randomnoise_output.mid')

