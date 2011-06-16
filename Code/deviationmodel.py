# Take a score and deviation file as input.
# Parse the score in music21
# Iterate through every note of the score
# Find corresponding note in deviationdata
# Create performance features vector
# Hash an encoding string for note and measure store performance features in dictionary

import music21 as m21
import re, os
import database as db
from representation import *
from BeautifulSoup import *

class Deviations:

  def __init__(self, tempo, tempo_deviations, note_deviations):
    self.tempo = tempo
    self.tempo_deviations = tempo_deviations
    self.note_deviations = note_deviations



def note_deviations(deviation):
  print "Reading deviations file"
  f = open(deviation)
  devfile = f.read()
  soup = BeautifulStoneSoup(devfile)
  print "Reading target score"
  f = open(os.path.dirname(deviation) + '/' + soup.deviation['target'])
  targetfile = f.read()
  target = BeautifulStoneSoup(targetfile)

  
  print "Constructing measures dictionary"
  measures = {}
  for measure in target.findAll('measure'):
    measures[str(measure['number'])] = measure

  print "Parsing deviations"
  tags = soup.findAll('note-deviation') + soup.findAll('miss-note')
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
#    print '========='
#    print m.group(3)
#    for n in notes:
#      print n
#      print '++++++'
#    print '---------'
#    print tag
    pitch = '{0}{1}{2}'.format(note.pitch.step.contents[0], alteration, note.pitch.octave.contents[0])

    key = "{0},{1},{2},{3},{4}".format(m.group(1), m.group(2), voice, pitch, number)
    #print key
    #print tag.attrs[0][1]
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

  tempo = soup.findAll('tempo')
  if len(tempo) > 1: print "More than one tempo tag found. Fix your code."
  tempo = float(tempo[0].contents[0])
  tags = soup.findAll('measure')
  tempo_deviations = {}
  for tag in tags:
    beats = tag.findAll('control')
    beatdevs = []
    # This assumes that beats contains the beats in order
    for beat in beats:
      if(beat.find('tempo-deviation')):
        beatdevs.append(float(beat.find('tempo-deviation').contents[0]))
    key = "{0}".format(tag.attrs[0][1])
    tempo_deviations[key] = beatdevs
  return Deviations(tempo, tempo_deviations, note_deviations)

def get_expressive_time(beat_lengths, measure_beat):
  multiplier = measure_beat - int(measure_beat)
  beat_lengths.append(0)
  return sum([beat_lengths[i] for i in range(0, int(measure_beat))]) + \
      multiplier * beat_lengths[int(measure_beat)]

def get_expressive_duration(beat_lengths, begin, duration):
  relevant_beats = beat_lengths[int(begin):int(begin+duration+1)]
  if int(begin) != begin:
    rest = int(begin) + 1.0 - begin
    if begin + duration < 1.0:
      return duration * relevant_beats[0]
    relevant_beats[0] *= rest
    duration = 1 + duration - rest
  return get_expressive_time(relevant_beats, duration)




def generate_performance(score, deviations):
  output = NoteList()
  bpm = deviations.tempo
  measure_length = 0.0
  perflength=0
  for part in score:
    performance_time = 0.0
    measure_length = 0.0
    if not isinstance(part,m21.stream.Part): continue
    for measure in part:
      if not isinstance(measure,m21.stream.Measure): continue

      tempo_devs = deviations.tempo_deviations['{0}'.format(measure.number)]
      beat_lengths = []

      performance_time += measure_length
      #if counter < 3:
      #  measure_length
      #  print performance_time
      #  counter += 1

      for dev in tempo_devs:
        beat_lengths.append(60000000 / (bpm * dev))

      measure_length = get_expressive_time(beat_lengths,len(tempo_devs))

      #print 'a'
      #if not len(tempo_devs) == measure.timeSignature.numerator:
      #  print "Time signature ({0}) numerator doesn't match number of beats in dev file ({1})?".format(str(measure.timeSignature), len(tempo_devs))

      for voice in measure:
        if not isinstance(voice,m21.stream.Voice): continue
        notes = 0
        measure_time = 0.0
        for note in voice:
          queue = {}
          if note.isRest:
            measure_time += note.duration.quarterLength
            continue
          elif isinstance(note,m21.note.Note):
            queue[str(note.pitch)] = note
          elif isinstance(note,m21.chord.Chord):
            for pitch in note.pitches:
              current = m21.note.Note()
              current.pitch = pitch
              current.duration = note.duration
              queue[str(pitch)] = current
          else: continue

          for n in queue.values():
            perflength += 1
            for i in range(0, len(queue)):
              query = "P1,{0},{1},{2},{3}".format(measure.number, str(voice.id), str(n.pitch), notes + i)
              if query in deviations.note_deviations: break 
            if not query in deviations.note_deviations:
              print "Note in score not found in deviations"
              #print query
              #on = performance_time + get_expressive_time(beat_lengths, measure_time)
              #off = on + get_expressive_duration(beat_lengths, measure_time, n.duration.quarterLength)
              #on = output.microseconds_to_ticks(on)
              #off = output.microseconds_to_ticks(off)
              #outnote = Note(on, off, n.pitch.midi, 80, 0)
              #output.insert(outnote)
              continue
            else:
              n_dev = deviations.note_deviations[query]
            if n_dev == 'miss':
              n_dev = (0, 0, 1, 1)
            attack = n_dev[0]
            release = n_dev[1]
            dynamics = n_dev[2]
            end_dynamics = n_dev[3]

            # Temporary solution
            onvel = dynamics * 100.0

            index = (int(measure_time))
            if index == measure_time:
              index -= 1
            on = performance_time + get_expressive_time(beat_lengths, measure_time) + attack * (60000000/bpm)
            off = on + get_expressive_duration(beat_lengths, measure_time, n.duration.quarterLength) + release * (60000000/bpm)


            # Convert on and off to ticks
            on = output.microseconds_to_ticks(on)
            off = output.microseconds_to_ticks(off)

            outnote = Note(on, off, n.pitch.midi, int(onvel), 0)
            output.insert(outnote)
          notes += len(queue.keys())
          measure_time += note.duration.quarterLength
  print perflength
  return output



def test():
  devpath = db.sampleDeviationPath()

  print "Extracting deviations"
  deviations = note_deviations(devpath)
  print "Loading score"
  score = db.sampleScore()
  score.flat.stripTies() 

  print "Generating performance"
  nlist = generate_performance(score, deviations)
  output = open('temp.txt', 'w')
  import sequencer as seq
  sequencer = seq.Sequencer()
  sequencer.play(nlist)

if __name__ == '__main__':
  test()
  limit = 10
  selection = db.select()
  #score = NoteList(db.getScoreMidiPath1(selection)).splice(0, 10)
  score = m21.converter.parse(db.getScorePath1(selection))
  score.partsToVoices()
  a = []
  counter = 0
  for x in score:
    if not isinstance(x, m21.stream.Part):
      continue
    for y in x:
      if not isinstance(y, m21.stream.Measure):
        continue
      for z in y:
        if not isinstance(z, m21.stream.Voice):
          continue
        for note in z:
          if counter >= limit:
            break
          if isinstance(note, m21.note.Note):
            a.append(note.midi)
            counter += 1

  performance = NoteList(db.getPerformancePath1(selection)).splice(0, limit)
  #a = score.simplelist()

  b = performance.simplelist()
  print a
  print b
  import minimumeditdistance as med
  alignment = med.match(a,b)
  first = performance.ticks_to_milliseconds(performance[0].on)
  for key in alignment:
    print "Score\t\t: {0}".format(score.ticks_to_milliseconds(score[key].on))
    print "Performance\t: {0}".format(performance.ticks_to_milliseconds(performance[alignment[key]].on) - first)


