#!/usr/env/python

from music21 import *
import sys, math



def replaceEights(score):
  for i in range(len(score)):
    if isinstance(score[i], note.Note):
      print score[i].fullName
      if(score[i].quarterLength == 0.25):
        score[i].quarterLength = 2
    elif isinstance(score[i], stream.Score) or \
        isinstance(score[i], stream.Part) or \
        isinstance(score[i], stream.Measure):
      replaceEights(score[i])

def averagePitch(score):
  pitches = []
  for i in range(len(score)):
    if isinstance(score[i], stream.Part):
      for j in range(len(score[i])):
        if isinstance(score[i][j], stream.Measure):
          for k in range(len(score[i][j])):
            if isinstance(score[i][j][k], note.Note):
              n = score[i][j][k]
              pitches.append(n.frequency)
  return sum(pitches)/len(pitches)

def higherIsFaster(score):
  scale = 10000
  print "Calculating average pitch"
  avg = averagePitch(score)
  print "Average pitch: {0}".format(avg)
  print "Adding expression"
  for i in range(len(score)):
    if isinstance(score[i], stream.Part):
      for j in range(len(score[i])):
        if isinstance(score[i][j], stream.Measure):
          for k in range(len(score[i][j])):
            if isinstance(score[i][j][k], note.Note):
              n = score[i][j][k]
              height = n.frequency
              diff = height - avg
              speedup = math.pow(diff/scale, 3.0) + 1.0
              print speedup
              score[i][j][k].quarterLength *= speedup




  
if __name__ == '__main__':
  print "Importing score"
  score = converter.parse(sys.argv[1])
  print "Doing stuff"
  higherIsFaster(score)
  print "Storing result"
  ofile = open('output.xml', 'w')
  ofile.write(score.musicxml)
#  score.show()


def toNoteStream(score):
  s = stream.Stream()
  for i in range(len(score)):
    if isinstance(score[i], note.Note):
      s.append(note)
    elif isinstance(score[i], stream.Score) or \
        isinstance(score[i], stream.Part) or \
        isinstance(score[i], stream.Measure):
      s += toNoteStream(score[i])
#      s_prime = toNoteStream(score[i])
#      if not s_prime is None:
#        s += s_prime
  s.show()
  return s

#notes = toNoteStream(score)
#notes.show()

  
#for i in range(len(score)):
#  if score[i] isinstance note.Note():
#  part = score[i]
#  for j in range(len(part)):
#    measure = part[j]
#    for k in range(len(measure)):
#      s.append(measure[k])

