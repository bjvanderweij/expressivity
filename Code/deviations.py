from representation import *
from music21 import *
from BeautifulSoup import *
import os, pickle

class Deviations:

  def __init__(self, deviation=None, target=None):
    if not deviation or not target:
      self.bpm = 120
      self.target = target
      self.init_silence = 0
      self.tempo_deviations = {}
      self.note_deviations = {}
      self.measure_lengths = {}
      return
    dir = target.split('/')[-2]
    name = target.split('/')[-1].split('.')[0]
    targetname = '{0}/{1}'.format(dir, name)
    if os.path.exists('deviations/{0}'.format(targetname)):
      print "Stored deviations found, remove deviations/{0} to create new ones".format(targetname)
      f = open('deviations/{0}'.format(targetname), 'rb')
      self.data = pickle.load(f)
    else:
      self.data = self.parse(deviation, target)
      self.store(dir, name)
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

  def store(self, dir, name):
    if not os.path.exists('deviations/{0}'.format(dir)):
      os.mkdir('deviations/{0}'.format(dir))
    location = 'deviations/{0}/{1}'.format(dir, name)
    print "Storing deviations in: {0} for future reference".format(location)
    f = open(location, 'wb')
    pickle.dump(self.data, f)

  # Parse a deviation file into a measurelength, tempo_deviations and note_deviations dict
  # It also reads the base tempo and should read the base dynamics
  def parse(self, deviation, targetpath):
    print "Reading deviations file"
    f = open(deviation)
    devfile = f.read()
    # We need to look up some information in the score file as this information is lost
    # in translation when the score is parsed with music21
    soup = BeautifulStoneSoup(devfile)
    print "Reading target score"
    f = open(targetpath)
    targetfile = f.read()
    target = BeautifulStoneSoup(targetfile)

    # For speed: put all measure tags in a dictionary
    print "Constructing measures dictionary"
    measures = {}
    for measure in target.findAll('measure'):
      measures[str(measure['number'])] = measure

    print "Parsing deviations"
    tags = soup.find('notewise').findAll('note-deviation') + soup.find('notewise').findAll('miss-note')
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
      # Count the number of notes in the measure and skip rests, grace notes and tied notes
      for n in notes[0:int(m.group(3))-1]:
        if n.rest: continue
        if n.grace: continue
        if n.tie and n.tie['type'] != 'start':
          continue
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
      #if m.group(2) == '3':
      #  print key
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
          key = (int(float(tag['number'])), int(float(beat['beat']))-1)
          value = float(beat.find('tempo-deviation').contents[0])
          tempo_deviations[key] = value
      measure_lengths[int(tag['number'])] = measurelength

    return {'tempo':tempo, 'tempo_deviations':tempo_deviations,\
        'note_deviations':note_deviations, 'measure_lengths':measure_lengths,\
        'init-silence':float(soup.deviation['init-silence']),'target':soup.deviation['target'],\
        'basedynamics':100.0}

#  def getBeatDuration(self, measure=None, beat=None):
#    if not measure and not beat:
#      return 60000000 / self.bpm
#    if not (int(measure), int(beat)) in self.tempo_deviations:
#      print "No tempo deviation found for measure {0}, beat {1}".format(measure, beat)
#      return None
#    return 60000000 / (self.bpm * self.tempo_deviations[(int(measure), int(beat))])
#
#  # beat expressed in quarternotes
#  def getExpressiveTime(self, measure, beat):
#    beat_lengths = []
#    for b in range(int(beat)+1):
#      if not self.getBeatDuration(measure,b):
#        beat_lengths.append(self.getBeatDuration())
#      else:
#        beat_lengths.append(self.getBeatDuration(measure, b))
#
#    multiplier = beat - int(beat)
#    beat_lengths.append(0)
#    if int(beat) >= len(beat_lengths):
#      print "measure: {0} beat:{1} bl:{2}".format(measure, beat, beat_lengths)
#    return sum([beat_lengths[i] for i in range(0, int(beat))]) + \
#        multiplier * beat_lengths[int(beat)]

  # Custom beat lengths list
  def getExpressiveTime1(self, beat_lengths, beat):
    multiplier = beat - int(beat)
    beat_lengths.append(0)
    return sum([beat_lengths[i] for i in range(0, int(beat))]) + \
        multiplier * beat_lengths[int(beat)]

  def getBeatDuration(self, measure=None, startbeat=None):
    incremental_measure = measure
    beat = startbeat
    if not measure and not beat:
      return 60000000 / float(self.bpm)
    while not (int(incremental_measure), int(beat)) in self.tempo_deviations:
      beat -= self.measure_lengths[incremental_measure]
      incremental_measure += 1
      if not incremental_measure in self.measure_lengths or beat < 0:
        print "No tempo deviation found for measure {0}, beat {1}".format(measure, startbeat)
        return None
    return 60000000 / (self.bpm * self.tempo_deviations[(int(incremental_measure), int(beat))])

  # beat expressed in quarternotes
  def getExpressiveTime(self, measure, beat):
    beat_lengths = []
    if beat > self.measure_lengths[measure]:
      print "WARNING: beat {0} exceeds measure length {1}, assuming last tempo deviation".format(beat, self.measure_lengths[measure])
    
    lastduration = self.getBeatDuration()
    for b in range(int(beat)+1):
      duration = self.getBeatDuration(measure, b)
      if not duration:
        duration = lastduration
      beat_lengths.append(duration)
      lastduration = duration

    multiplier = beat - int(beat)
    beat_lengths.append(0)
    if int(beat) >= len(beat_lengths):
      print "measure: {0} beat:{1} bl:{2}".format(measure, beat, beat_lengths)
    return sum([beat_lengths[i] for i in range(0, int(beat))]) + \
        multiplier * beat_lengths[int(beat)]

  # Begin and duration expressed in quarternotes
  def getExpressiveSimpleDuration(self, measure, begin, duration):
    return self.getBeatDuration(measure, int(begin)) * duration

  #Complex
  def getExpressiveDuration(self, measure, begin, duration):
    beat_lengths = []
    while len(beat_lengths) < duration + begin:
      for b in range(self.measure_lengths[measure]):
        beatduration = self.getBeatDuration(measure, b)
        if not beatduration:
          beatduration = 1
        beat_lengths.append(beatduration)
      measure += 1
    relevant_beats = beat_lengths[int(begin):int(begin+duration+1)]
    if int(begin) != begin:
      rest = int(begin) + 1.0 - begin
      if begin + duration < 1.0:
        return duration * relevant_beats[0]
      relevant_beats[0] *= rest
      duration = 1 + duration - rest
    return self.getExpressiveTime1(relevant_beats, duration)
      
