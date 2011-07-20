import music21 as m21
import os, pickle, util, scorefeatures
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

def savePerformance(selection, expression, f):
  ofile = open('expressiveperformances/{0}'.format(f), 'wb')
  pickle.dump((selection, expression), ofile)


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
  m = open('data/{0}/metadata'.format(name), 'wb')

  metadata = {'version':scorefeatures.version, 'featureset':scorefeatures.featureset}
  pickle.dump(features, f)
  pickle.dump(expression, e)
  pickle.dump(metadata, m)

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

def loadPerformance(name=None):
  if not name:
    choice = util.menu('Pick a performance', os.listdir('expressiveperformances'))
    name = os.listdir('expressiveperformances')[choice]
  f = open('expressiveperformances/{0}'.format(name), 'rb')
  return pickle.load(f) 

def loadFeatures(name):
  f = open('data/{0}/features'.format(name), 'rb')
  e = open('data/{0}/expression'.format(name), 'rb')
  m = open('data/{0}/metadata'.format(name), 'rb')

  return (pickle.load(f), pickle.load(e), pickle.load(m))
  
def chooseFeatures():
  choice = util.menu('Pick a dataset', ['Name:\t[{0}]\tInfo:\t{1}'.format(x, corpusInfo(x)) for x in os.listdir('data')])
  return loadFeatures(os.listdir('data')[choice])

def datasets():
  return os.listdir('data')


def extendedCorpusInfo(name):
  (f, e, m) = loadFeatures(name)
  version = m['version']
  featureset = m['featureset']
  unique = {}
  print '============================================'
  for work in f:
    unique[(work[0], work[1])] = unique.get((work[0], work[1]), []) + [work[2]]
  for work in unique:
    print '{0}: {1}'.format(work, unique[work])
  print '============================================'
  for work in f:
    features = f[work]
    notes = 0
    if 'const_length' in featureset:
      index = featureset.index('const_length')
      notes += sum([x[index] for x in features])
    else:
      # Some featureset strings miss the const_lenght index
      # This code crashes if the featureset truly doesn't have this feature
      notes += sum([x[12] for x in features])
    print '{0}: notes: {1} const: {2}'.format(work, notes, len(features))

def corpusInfo(name):
  (f, e, m) = loadFeatures(name)
  avg_notes = 0
  size = 0
  version = m['version']
  featureset = m['featureset']
  unique = {}
  for work in f:
    size += len(f[work])
    unique[(work[0], work[1])] = 0
    # This only works for corpora that have a const length feature
    if 'const_length' in featureset:
      index = featureset.index('const_length')
      avg_notes += sum([x[index] for x in f[work]])
    else:
      # Some featureset strings miss the const_lenght index
      # This code crashes if the featureset truly doesn't have this feature
      avg_notes += sum([x[12] for x in f[work]])
  avg_notes /= float(size)
  return '[Works: {4}\tPerformances: {0}\tEntries: {1}\tFeatures version: {2}\tNotes per entry: {3}]'.format(len(f), size, version, avg_notes, len(unique))

# This doesn't handle polyfony very well but it is used for single voices only anyway
def newParseScore(score):
  midifile = score.midiFile
  midifile.open('/tmp/tmp.mid', 'wb')
  midifile.write()
  midifile.close()
  return NoteList('/tmp/tmp.mid')
  
def parseScore(score, measures=None):
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
      if measures:
        if not measure.number in measures:
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
    return '[ {0}]'.format(' '.join([recursive_print(x) for x in l]))
  else:
    if hasattr(l,'name'):
      return l.name()
    else:
      return l

# Least squares fit
def linear_fit(X, Y):
  n = len(X)
  if len(X) != len(Y):
    print "linear fit: WARNING: lengths of data don't match: {0} and {1}".format(len(X), len(Y))
  sum_x=0.0
  sum_y=0.0
  sum_xx=0.0
  sum_xy=0.0
  for x,y in zip(X,Y):
    sum_x=sum_x+x
    sum_y=sum_y+y
    xx=pow(x,2)
    sum_xx=sum_xx+xx
    xy=x*y
    sum_xy=sum_xy+xy

  #Calculating the coefficients
  a=(-sum_x*sum_xy+sum_xx*sum_y)/float(n*sum_xx-sum_x*sum_x)
  b=(-sum_x*sum_y+n*sum_xy)/float(n*sum_xx-sum_x*sum_x)
  return a, b
