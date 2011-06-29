from representation import *
from BeautifulSoup import *
from deviations import *
from score import *
import music21 as m21
import pickle

class Alignment:

  def __init__(self, scorepath, deviations):
    print "Creating alignment"
    # Storing this object is not possible, score id's change and Scores are not pickleable :(
    self.deviations = deviations
    # Am I really writing ugly code like this? Apparently I am
    if isinstance(scorepath,str):
      self.score = m21.converter.parse(scorepath)
    else:
      self.score = scorepath
    # This doesn't actually remove ties, but it does fix the duration of tied notes
    self.score = self.score.stripTies()
    # Remove all tied notes except the start notes
    self.removeTies()
    self.alignment = None
    self.align()

    #  self.storeAlignment()
    print "Done"

  def removeTies(self):
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
            if isinstance(note, m21.chord.Chord) or isinstance(note, m21.note.Note):
              if hasattr(note,'tie') and note.tie is not None:
                if not note.tie.type == 'start':
                  voice.remove(note)
                else:
                  note.tie = None


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
    print self.score, self.score[0]
    s = Score(self.score)
    return s.melody()

  def expressiveMelody(self):
    return self.performance(self.melody())

  def melodyPerformance(self):
    return self.performance(self.score, self.melody())

  def performance(self, score=None, melody=None):
    print "Creating performance"
    if not score:
      score = self.score
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
            #if hasattr(note,'tie') and note.tie is not None and note.tie.type is not 'start':
            #  continue
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
                  melodyvoice = melody[1][part.index(measure)].getElementById(1)
                  if melodyvoice:
                    melodynote = melodyvoice.getElementsByOffset(note.offset)[0]
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
                        melodyvoice = melody[1][index].getElementById(1)
                        if melodyvoice:
                          melodynote = melodyvoice.getElementsByOffset(0, barduration)[0]
                      except IndexError:
                        pass
                    else: 
                      melodynote = lastmelodynote
                  if measure.number < 4:
                    print "{0} {1} {2}".format(note, melodynote, note.offset)
                  if not (melodynote.id, str(melodynote.pitch)) in self.alignment:
                    print '{0} {1}'.format(measure.number, melodynote.offset)
                    deviation = None
                  deviation = self.alignment[melodynote.id, str(melodynote.pitch)]
                  if not deviation: continue
                  # Attack and release should be zero in this case
                  deviation = (0, 0, deviation[2], deviation[3])
                else:
                  deviation = self.alignment[melodynote.id, str(melodynote.pitch)]
                lastmelodynote = melodynote
              else:
                if not (note.id, str(n.pitch)) in self.alignment:
                  print '{0} {1}'.format(measure.number, note.offset)
                  deviation = None
                deviation = self.alignment[note.id, str(n.pitch)]
              if not deviation: 
                continue

                  
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
              
              pnote = Note(on, off, n.pitch.midi, int(onvel), int(offvel), 
                  annotation=(score.index(part), part.index(measure), measure.index(voice), voice.index(note), note.id))
              performance.insert(pnote)
    return performance

  def getDeviations(self,note):
    return self.alignment[note.id, str(note.pitch)]

  def align(self):
    deviations = self.deviations
    score = self.score
    print "{0} {1}".format(len(score.flat.notes), len(score.flat.stripTies().notes))
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
            #if hasattr(note,'tie') and note.tie is not None and note.tie.type is not 'start':
            #  if isinstance(note, m21.chord.Chord):
            #    notes += len(note.pitches) - 1
            #  notes += 1
            #  continue
            elif isinstance(note,m21.note.Note):
#              if not note.id in 
              queue[str(note.pitch)] = note
            elif isinstance(note,m21.chord.Chord):
              for pitch in note.pitches:
                current = m21.note.Note()
                current.pitch = pitch
                current.duration = note.duration
                queue[str(pitch)] = current
            else: continue
            for n in queue.values():
              for i in range(len(queue)):
                query = "P1,{0},{1},{2},{3}".format(measure.number, str(voice.id), str(n.pitch), notes + i)
                if query in deviations.note_deviations: break 
              # This situation is usually caused by fucking TIED NOTES, it can mess up indexing
              if not query in deviations.note_deviations:
                print "Query: {0} not found in deviations".format(query)
                n_dev = None
              else:
                n_dev = deviations.note_deviations[query]
              if n_dev == 'miss':
                n_dev = None

              alignment[(note.id, str(n.pitch))] = n_dev
            notes += len(queue.keys())
    self.alignment = alignment

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

