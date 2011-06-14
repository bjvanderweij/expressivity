from representation import *
from music21 import *

# This class adds a useful measure_time, indication the onset time in quarternotes from the beginning of the measure
class AlignNote:

  def __init__(self, part, measure, voice, note, measure_time):
    # Music21 score index: m21.note.Note = score[part][measure][voice][note]
    self.part = part 
    self.measure = measure
    self.voice = voice
    self.note = note
    self.measure_time = measure_time


class Alignment:

  def __init__(self, score, deviations):
    self.score = score
# This line should come after parsing the deviations file
    self.alignment = align(score, deviations)
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

  def align(score, deviations)
    output = NoteList()
    bpm = deviations.tempo
    for part in score:
      if not isinstance(part,m21.stream.Part): continue
      for measure in part:
        if not isinstance(measure,m21.stream.Measure): continue
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
                n_dev = None
              else:
                n_dev = deviations.note_deviations[query]
              if n_dev == 'miss':
                n_dev = None

              alignnote = AlignNote(part,measure,voice,note,measure_time)
              alignment[alignnote = n_dev

            notes += len(queue.keys())
            measure_time += note.duration.quarterLength
    return alignment

