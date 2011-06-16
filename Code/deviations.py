from representation import *
from music21 import *
from BeautifulSoup import *
import os, pickle

class Deviations:

  def __init__(self, deviation, target):
    targetname = os.path.split(target)[1].split('.')[0]
    if targetname in os.listdir('deviations'):
      print "Stored deviations found, remove deviations/{0} to create new ones".format(targetname)
      f = open('deviations/{0}'.format(targetname), 'rb')
      self.data = pickle.load(f)
      print "Loaded"
    else:
      self.data = self.parse(deviation, target)
      self.store(targetname)
    self.bpm = self.data['tempo']
    self.tempo_deviations = self.data['tempo_deviations']
    self.note_deviations = self.data['note_deviations']
    self.measure_lengths = self.data['measure_lengths']
    # init silence in seconds
    self.init_silence = self.data['init-silence']
    # Target musicxml score
    self.target = self.data['target']

    # When should be extracted from soup, default=100
    self.basedynamics = self.data['basedynamics']

  def store(self, name):
    location = 'deviations/{0}'.format(name)
    print "Storing deviations in: {0} for future reference".format(location)
    f = open(location, 'wb')
    pickle.dump(self.data, f)

  def parse(self, deviation, targetpath):
    print "Reading deviations file"
    f = open(deviation)
    devfile = f.read()
    soup = BeautifulStoneSoup(devfile)
    print "Reading target score"
    f = open(targetpath)
    targetfile = f.read()
    target = BeautifulStoneSoup(targetfile)

    print "Constructing measures dictionary"
    measures = {}
    for measure in target.findAll('measure'):
      measures[str(measure['number'])] = measure

    print "Parsing deviations"
    tags = soup.find('partwise').findAll('note-deviation') + soup.find('partwise').findAll('miss-note')
    note_deviations = {}
    pointerexp = re.compile('@id=\'(.*)\'\]/measure\[\@number=\'(.*)\'\]/note\[(.*)\]')

    for tag in tags:
      m = re.search(pointerexp, tag.attrs[0][1])
      if not m: 
        print "xpointer reference didn't match, bug in code or bug in deviation file"
        continue
      # Find the voice and notenumber in that voice
      measure = measures[m.group(2)]
      notes = measure.findAll('note')
      note = notes[int(m.group(3)) - 1]
      voice = note.voice.contents[0]

      # Instead of continuing, add gracenotes to stream here?
      if note.grace: continue
      number = 0
      for n in notes[0:int(m.group(3))-1]:
        if n.rest: continue
        if n.grace: continue
        if n.voice.contents[0] == voice:
          number += 1

      alteration = ''
      if note.alter:
        if note.alter.contents[0] == '1':
          alteration = '#'
        elif note.alter.contents[0] == '-1':
          alteration = '-'
      pitch = '{0}{1}{2}'.format(note.pitch.step.contents[0], alteration, note.pitch.octave.contents[0])

      key = "{0},{1},{2},{3},{4}".format(m.group(1), m.group(2), voice, pitch, number)
      if tag.name == 'miss-note': 
        value = 'miss'
      else:
        value = (\
            float(tag.attack.contents[0]),\
            float(tag.release.contents[0]),\
            float(tag.dynamics.contents[0]),\
            float(tag.contents[3].contents[0]),\
          )
      note_deviations[key] = value

    tempo = soup.find('non-partwise').findAll('tempo')
    if len(tempo) > 1: print "More than one tempo tag found. Fix your code."
    tempo = float(tempo[0].contents[0])
    tags = soup.find('non-partwise').findAll('measure')
    tempo_deviations = {}
    measure_lengths = {}

    for tag in tags:
      beats = tag.findAll('control')
      # This assumes that beats contains the beats in order
      measurelength = 0
      for beat in beats:
        if beat.find('tempo-deviation'):
          measurelength += 1
          tempo_deviations[(int(float(tag['number'])), int(float(beat['beat']))-1)] = float(beat.find('tempo-deviation').contents[0])
      if measurelength == 0:
        print tag['number']
      measure_lengths[int(tag['number'])] = measurelength

    return {'tempo':tempo, 'tempo_deviations':tempo_deviations,\
        'note_deviations':note_deviations, 'measure_lengths':measure_lengths,\
        'init-silence':float(soup.deviation['init-silence']),'target':soup.deviation['target'],\
        'basedynamics':100.0}

  def getBeatDuration(self, measure, beat):
    return 60000000 / (self.bpm * self.tempo_deviations[(int(measure), int(beat))])

  # beat expressed in quarternotes
  def getExpressiveTime(self, measure, beat):
    beat_lengths = []
    for b in range(self.measure_lengths[measure]):
      beat_lengths.append(self.getBeatDuration(measure, b))

    multiplier = beat - int(beat)
    beat_lengths.append(0)
    if int(beat) >= len(beat_lengths):
      print "{0} {1}".format(beat, beat_lengths)
    return sum([beat_lengths[i] for i in range(0, int(beat))]) + \
        multiplier * beat_lengths[int(beat)]

  # Custom beat lengths list
  def getExpressiveTime1(self, beat_lengths, beat):
    multiplier = beat - int(beat)
    beat_lengths.append(0)
    return sum([beat_lengths[i] for i in range(0, int(beat))]) + \
        multiplier * beat_lengths[int(beat)]

  # Begin and duration expressed in quarternotes
  def getExpressiveSimpleDuration(self, measure, begin, duration):
    return self.getBeatDuration(measure, int(begin)) * duration

  #Complex
  def getExpressiveDuration(self, measure, begin, duration):
    return self.getBeatDuration(measure, int(begin)) * duration
    beat_lengths = []
    for b in range(self.measure_lengths[measure]):
      beat_lengths.append(self.getBeatDuration(measure, b))

    relevant_beats = beat_lengths[int(begin):int(begin+duration+1)]
    if int(begin) != begin:
      rest = int(begin) + 1.0 - begin
      if begin + duration < 1.0:
        return duration * relevant_beats[0]
      relevant_beats[0] *= rest
      duration = 1 + duration - rest
    return self.getExpressiveTime1(relevant_beats, duration)
      
