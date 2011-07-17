from representation import *
from BeautifulSoup import *
from deviations import *
from score import *
import music21 as m21
import pickle, copy

class Alignment:

  def __init__(self, scorepath, deviations, noAlign=False):
    print "Creating alignment"
    # Storing this object is not possible, score id's change and Scores are not pickleable :(
    self.deviations = deviations
    # Am I really writing ugly code like this? Apparently I am
    if isinstance(scorepath,str):
      self.score = m21.converter.parse(scorepath)
    else:
      self.score = scorepath
    import score

    s = score.Score(self.score)
    self.m = s.melody()
    self.m = score.Score(self.m).tieless()
    self.s = s.tieless()
    if not noAlign:
      self.alignment = None
      self.align()
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
    return self.m

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
    lastdeviation = (0, 0, 1, 1)
    for part in score.parts:
      measureduration = 0.0
      performancetime = begintime
      for measure in part:
        if not isinstance(measure,m21.stream.Measure): continue
        #if melody: print "Bar {0} done".format(measure.number)
        performancetime += measureduration
        measureduration = self.deviations.getExpressiveTime(measure.number, measure.barDuration.quarterLength)
        for voice in measure.voices:
          for note in voice.notes:
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
                # 
                try:
                  melodyvoice = melody[1][part.index(measure)].getElementById(1)
                  if melodyvoice:
                    melodynote = melodyvoice.getElementsByOffset(note.offset)[0]
                    if not isinstance(melodynote, m21.note.Note):
                      melodynote = None
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
                  #if measure.number < 4:
                  #  print "{0} {1} {2}".format(note, melodynote, note.offset)
                  if not (melodynote.id, str(melodynote.pitch)) in self.alignment:
                    print '{0} {1}'.format(measure.number, melodynote.offset)
                    deviation = None
                  deviation = self.alignment[melodynote.id, str(melodynote.pitch)]
                  if not deviation: continue
                  # Attack and release should be zero in this case
                  deviation = (0, 0, deviation[2], deviation[3])
                else:
                  if not (melodynote.id, str(melodynote.pitch)) in self.alignment:
                    print '{0} {1}'.format(measure.number, melodynote.offset)
                  deviation = self.alignment[melodynote.id, str(melodynote.pitch)]
                lastmelodynote = melodynote
              else:
                if not (note.id, str(n.pitch)) in self.alignment:
                  # This is a note that was not found in the deviations
                  #print '{0} {1}'.format(measure.number, note.offset)
                  deviation = None
                else:
                  deviation = self.alignment[note.id, str(n.pitch)]
              if not deviation: 
                deviation = lastdeviation
              lastdeviation = deviation
              #if note.offset == 6.25:
              #  print measure.duration
              #if note.offset > measure.duration.quarterLength:
              #  print "Note offset larger than measurelength, setting to last beat"
              #  note.offset = measure.duration.quarterLength
                 
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
              if off < on:
                print "WARNING: release before onset! Check your deviations or performancerenderer"
                off = on
              
              pnote = Note(on, off, n.pitch.midi, int(onvel), int(offvel), 
                  annotation=(score.index(part), part.index(measure), measure.index(voice), voice.index(note), note.id))
              performance.insert(pnote)
    return performance

  def getDeviations(self,note):
    return self.alignment[note.id, str(note.pitch)]

  def align(self):
    deviations = self.deviations
    #score = copy.deepcopy(self.score)
    score = self.score
    bpm = deviations.bpm
    alignment = {}
    # Assume two part music
    p1 = score.parts[0]
    p2 = score.parts[1]
    p1measures = []
    p2measures = []
    for m in p1:
      if isinstance(m, m21.stream.Measure):
        p1measures.append(m)
    for m in p2:
      if isinstance(m, m21.stream.Measure):
        p2measures.append(m)
    for p1measure,p2measure in zip(p1measures, p2measures):
      mergedvoices = []
      if p1measure.number != p2measure.number:
        print "This shouldn't happen!"
      voices = [v for v in p1measure.voices] + [v for v in p2measure.voices]
      for voice in voices:
        if voice.id in [v.id for v in mergedvoices]:
          index = 0
          for i in range(len(mergedvoices)):
            if mergedvoices[i].id == voice.id: index = i
          for note in voice.notes:
            mergedvoices[index].insert(note)
        else:
          mergedvoices.append(voice)

      for voice in mergedvoices:
        notes = 0
        for note in voice.notes:
          #if int(voice.id) == 1 and int(p1measure.number) == 3:
          #  print "{0} {1}".format(note.pitch, note.offset)
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
              query = "P1,{0},{1},{2},{3}".format(p1measure.number, str(voice.id), str(n.pitch), notes + i)
              if query in deviations.note_deviations: break 
            # This situation is usually caused by fucking TIED NOTES, it can mess up indexing
            if not query in deviations.note_deviations:
              print "WARNING: Query: {0} not found in deviations".format(query)
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

