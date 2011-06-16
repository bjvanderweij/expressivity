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

  def melodyExpressionPerformance(self, melody):
    pass

  def performance(self, score, melody=None):
    performancetime = self.deviations.init_silence * 1000000.0
    performance = NoteList()
    count = 0
    for part in score:
      measureduration = 0.0
      performancetime = 0.0
      if not isinstance(part,m21.stream.Part): continue
      for measure in part:
        if not isinstance(measure,m21.stream.Measure): continue
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
              (deviation, measuretime) = self.alignment[note.id, str(n.pitch)]
              if not deviation:
                continue

              onvel = deviation[2] * self.deviations.basedynamics
              offvel = 0

              on_ms = performancetime + self.deviations.getExpressiveTime(measure.number, measuretime)
              off_ms = on_ms + self.deviations.getExpressiveDuration(measure.number, measuretime, n.duration.quarterLength)
              on_ms += deviation[0] * self.deviations.getBeatDuration(measure.number, int(measuretime))
              off_ms += deviation[1] * self.deviations.getBeatDuration(measure.number, int(measuretime))
              #off_ms += deviation[1] * self.deviations.getBeatDuration(measure.number, int(measuretime + n.duration.quarterLenghth))

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
          measure_time = 0.0
          notes = 0
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

              alignment[(note.id, str(n.pitch))] = (n_dev, measure_time)
            notes += len(queue.keys())
            measure_time += note.duration.quarterLength
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

