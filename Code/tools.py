import music21 as m21
import os, pickle, util
from representation import *

def savePDF(score, name):
  print "Saving to sheets/{0}.pdf".format(name)
  ofile = open('sheets/score.xml', 'w')
  ofile.write(score.musicxml)
  ofile.close()
  os.system('musescore sheets/score.xml -o sheets/{0}.pdf'.format(name))
  
def saveXML(score, name):
  print "Saving to scores/{0}.xml".format(name)
  ofile = open('scores/{0}.xml'.format(name), 'w')
  ofile.write(score.musicxml)
  ofile.close()

def saveFeatures(features, expression):
  while True:
    print "Enter a name for the directory"
    name = raw_input('')
    print "Confirm to save to: data/{0}/features and data/{0}/expression (Y/n)".format(name)
    answer = raw_input('')
    if not answer == 'Y' and not answer == '':
      continue
    if not os.path.exists('data/{0}'.format(name)):
      os.mkdir('data/{0}'.format(name))
      break
    else:
      print "Directory exists, overwrite? (y/N)"
      answer = raw_input('')
      if answer == 'y':
        break
  f = open('data/{0}/features'.format(name), 'wb')
  e = open('data/{0}/expression'.format(name), 'wb')
  pickle.dump(features, f)
  pickle.dump(expression, e)

def saveCSV(features, expression):
  while True:
    print "Enter a name for the file"
    name = raw_input('')
    print "Confirm to save to: data/{0}.csv (Y/n)".format(name)
    answer = raw_input('')
    if not answer == 'Y' and not answer == '':
      continue
    if not os.path.exists('data/{0}'.format(name)):
      break
    else:
      print "File exists, overwrite? (y/N)"
      answer = raw_input('')
      if answer == 'y':
        break
  out = open('data/{0}.csv'.format(name), 'w')
  for key in features.keys():
    f = features[key]
    e = expression[key]
    line = 'onset_arch, pitch_interval, duration_ratio, ioi_ratio, loudness_ratio, duration_ratio_exp\n'
    out.write(line)
    for fv, ev in zip(f,e):
      line = '{0},{1},{2},{3},{4},{5}\n'.format(fv[0],fv[2],fv[3],ev[0],ev[1],ev[3])
      out.write(line)
  out.close()


def loadFeatures(name):
  f = open('data/{0}/features'.format(name), 'rb')
  e = open('data/{0}/expression'.format(name), 'rb')
  return (pickle.load(f), pickle.load(e))
  
def chooseFeatures():
  choice = util.menu('Pick a dataset', os.listdir('data'))
  return loadFeatures(os.listdir('data')[choice])

# This doesn't handle polyfony very well but it is used for single voices only anyway
def newParseScore(score):
  midifile = score.midiFile
  midifile.open('/tmp/tmp.mid', 'wb')
  midifile.write()
  midifile.close()
  return NoteList('/tmp/tmp.mid')
  
def parseScore(score):
  output = NoteList() 
  defaultvelocity = 63
  for part in score.parts:
    # performancetime in quarternotes
    performancetime = 0.0
    measuretime = 0.0
    for measure in part:
      performancetime = measure.offset
      if not isinstance(measure, m21.stream.Measure):
        continue
      for voice in measure.voices:
        for note in voice:
          notes = []
          if isinstance(note,m21.chord.Chord):
            for pitch in note.pitches:
              n = m21.note.Note()
              n.pitch = pitch
              n.duration = note.duration
              notes.append(n)
          elif isinstance(note,m21.note.Note):
            notes = [note]
          for n in notes:
            output.insert(Note(\
                output.quarternotes_to_ticks(performancetime + note.offset),\
                output.quarternotes_to_ticks(performancetime + note.offset + note.duration.quarterLength),\
                n.pitch.midi, defaultvelocity,\
                annotation=(score.index(part), part.index(measure), measure.index(voice), voice.index(note), note.id)))
  return output

def recursive_print(l):
  if hasattr(l,'__iter__'):
    return '({0})'.format(','.join([recursive_print(x) for x in l]))
  else:
    if hasattr(l,'name'):
      return l.name()
    else:
      return l

