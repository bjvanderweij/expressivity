from representation import *
from BeautifulSoup import *
from deviations import *
from score import *
import music21 as m21
import pickle

# This class adds a useful measure_time, indication the onset time in quarternotes from the beginning of the measure
class AlignNote:

  def __init__(self, ID, pitch, measure_time):
    self.ID = ID
    self.pitch = pitch
    self.measure_time = measure_time



class Alignment:

  def __init__(self, scorepath, deviations):
    print "Creating alignment"
    # Storing this object is not possible, score id's change and Scores are not pickleable :(
    self.deviations = deviations
    #if deviations.target.split('.')[0] in os.listdir('scores'):
    #  print "Stored score found, remove scores/{0} to create a new one".format(deviations.target.split('.')[0])
    #  f = open('scores/{0}'.format(deviations.target.split('.')[0]), 'rb')
    #  self.score = pickle.load(f)
    #else:
    self.score = m21.converter.parse(scorepath)
    #  self.storeScore()
    #if deviations.target.split('.')[0] in os.listdir('alignments'):
    #  print "Stored alignment found, remove alignments/{0} to create a new one".format(deviations.target.split('.')[0])
    #  f = open('alignments/{0}'.format(deviations.target.split('.')[0]), 'rb')
    #  self.alignment = pickle.load(f)
    #else:
    self.alignment = self.align(self.score, deviations)
    #  self.storeAlignment()
    self.score.flat.stripTies() 
    print "Done"

  def storeAlignment(self):
    location = 'alignments/{0}'.format(self.deviations.target.split('.')[0])
    print "Storing alignment in: {0} for future reference".format(location)
    f = open(location, 'wb')
    pickle.dump(self.alignment, f)

  def storeScore(self):
    location = 'scores/{0}'.format(self.deviations.target.split('.')[0])
    print "Storing alignment in: {0} for future reference".format(location)
    f = open(location, 'wb')
    pickle.dump(self.score, f)

  def getBPM(self):
    return self.deviations.bpm

  def getBeatDuration(self, measure, beat):
    return self.deviations.getBeatDuration(measure, beat)

  def melody(self):
    print self.score.id
    s = Score(self.score)
    return s.melody()

  def expressiveMelody(self):
    return self.performance(self.melody())

  def performance(self):
    return self.performance(self.score)

  def melodyPerformance(self, melody):
    return self.performance(self.score)

  def melodyPerformance(self):
    return self.performance(self.score, self.melody())

  def performance(self, score, melody=None):
    print "Creating performance"
    # I am not sure about the units in which init silence is expressed
    begintime = self.deviations.init_silence * 1000000.0
    #performancetime = self.deviations.init_silence * self.deviations.getBeatDuration()
    performance = NoteList()
    lastmelodynote = None
    count = 0
    for part in score:
      measureduration = 0.0
      performancetime = begintime
      if not isinstance(part,m21.stream.Part): continue
      for measure in part:
        if not isinstance(measure,m21.stream.Measure): continue
        if melody: print "Bar {0} done".format(measure.number)
        performancetime += measureduration
        measureduration = self.deviations.getExpressiveTime(measure.number, self.deviations.measure_lengths[measure.number])
        for voice in measure:
          if not isinstance(voice,m21.stream.Voice): continue
          for note in voice:
            queue = {}
            if note.isRest:
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
              # If a melody is defined we need to know if the current note is a melody note
              # If it is not, we need to know if it is played at the same time as a melody note
              # If this isn't the case, use the tempo curve for expression and some measure of dynamics(nearest melody note?)
              if melody:
                melodynote = None
                try:
                  melodynote = melody[1][part.index(measure)].getElementById(1).getElementsByOffset(note.offset)[0]
                  if measure.number < 4:
                    print "{0} {1} {2}".format(note, melodynote, note.offset)
                except IndexError:
                  pass
                if not melodynote or not isinstance(melodynote, m21.note.Note):
                  # Find the first melody note following this note(in this measure)    
                  # This should actually look for the NEAREST melody note because...
                  # IF THERE ARE NO MELODY NOTES OFTER THIS NOTE THIS CODE WILL FAIL
                  # This is now somewhat fixed, if no melodynote is found, the last melodynote is used
                  baroffset = 0
                  while not melodynote or not isinstance(melodynote, m21.note.Note):
                    index = part.index(measure) + baroffset
                    baroffset += 1
                    if index + baroffset < len(melody[1]):
                      if not isinstance(melody[1][index], m21.stream.Measure):
                        continue
                      barduration = melody[1][index].barDuration.quarterLength
                      try:
                        melodynote = melody[1][index].getElementById(1).getElementsByOffset(0, barduration)[0]
                      except IndexError:
                        pass
                    else: 
                      melodynote = lastmelodynote
                  if measure.number < 4:
                    print "{0} {1} {2}".format(note, melodynote, note.offset)
                  deviation = self.alignment[melodynote.id, str(melodynote.pitch)]
                  if not deviation: continue
                  # Attack and release should be zero in this case
                  deviation = (0, 0, deviation[2], deviation[3])
                else:
                  deviation = self.alignment[melodynote.id, str(melodynote.pitch)]
                lastmelodynote = melodynote
              else:
                deviation = self.alignment[note.id, str(n.pitch)]
              if not deviation: continue

                  
              onvel = deviation[2] * self.deviations.basedynamics
              offvel = 0
              on_ms = performancetime + self.deviations.getExpressiveTime(measure.number, note.offset)
              off_ms = on_ms + self.deviations.getExpressiveDuration(measure.number, note.offset, n.duration.quarterLength)
              beatduration = self.deviations.getBeatDuration(measure.number, int(note.offset))
              if not beatduration:
                beatduration = 1.0
              on_ms += deviation[0] * beatduration
              off_ms += deviation[1] * beatduration
              #off_ms += deviation[1] * self.deviations.getBeatDuration(measure.number, int(note.offset + n.duration.quarterLenghth))

              on = performance.microseconds_to_ticks(on_ms)
              off = performance.microseconds_to_ticks(off_ms)
              
              pnote = Note(on, off, n.pitch.midi, int(onvel), int(offvel))
              performance.insert(pnote)
    return performance

  def getDeviations(self,note):
    return self.alignment[note.id, str(note.pitch)]

  def note_ids(self):
    count = 0
    max = 20
    for part in self.score:
      if not isinstance(part, m21.stream.Part):
        continue
      for measure in part:
        if not isinstance(measure, m21.stream.Measure):
          continue
        for voice in measure:
          if not isinstance(voice, m21.stream.Voice):
            continue
          for note in voice:
            if count > max:
              break
            if isinstance(note, m21.note.Note):
              count += 1
              print '{0} {1}'.format(str(note), note.id)

  def align(self, score, deviations):
    output = NoteList()
    bpm = deviations.bpm
    alignment = {}
    for part in score:
      if not isinstance(part,m21.stream.Part): continue
      for measure in part:
        if not isinstance(measure,m21.stream.Measure): continue
        for voice in measure:
          if not isinstance(voice,m21.stream.Voice): continue
          notes = 0
          for note in voice:
            queue = {}
            if note.isRest:
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
              for i in range(0, len(queue)):
                query = "P1,{0},{1},{2},{3}".format(measure.number, str(voice.id), str(n.pitch), notes + i)
                if query in deviations.note_deviations: break 
              if not query in deviations.note_deviations:
                print "Query: {0} not found in deviations".format(query)
                n_dev = None
              else:
                n_dev = deviations.note_deviations[query]
              if n_dev == 'miss':
                n_dev = None

              alignment[(note.id, str(n.pitch))] = n_dev
            notes += len(queue.keys())
    return alignment

def run():
  import database as db
  selection = db.select()
  print ">>> Extracting deviations"
  deviations = db.getDeviation1(selection)
  print ">>> Loading score"
  score = db.getScorePath1(selection)
  print ">>> Loading alignment"
  alignment = Alignment(score, deviations)
  alignment.store("alignments/a1")
  print ">>> Generating performance"
  performance = alignment.performance()
  performance.exportMidi('output/generated.mid')
  #for n in performance[0:20]:
  #  print n.info()

  
  #output = open('temp.txt', 'w')
  #for n in nlist:
  #  output.write(str(n) + '\n')
  #output.close()
  import sequencer as seq
  sequencer = seq.Sequencer()
  sequencer.play(performance)
  
if __name__ == '__main__':
  run()

