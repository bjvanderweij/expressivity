import music21 as m21
import tools

class Score:

  def __init__(self, score):
    self.score = score
    # Assume each part has the same number of measures and every score has two parts
    parts = []
    for part in self.score:
      if isinstance(part,m21.stream.Part):
        parts.append(part)
    self.part1 = parts[0]
    self.part2 = parts[1]

  def notesOn(self,measure,beat):
    m1 = self.part1[measure]
    m2 = self.part2[measure]
  
  def getNoteList():
    return tools.parseScore(self.score)


  def note_ids(self):
    count = 0
    max = 10
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
              print '{0} {1}'.format(str(note), note.id)
              count += 1

  #Highest note at any moment
  def melody(self):
    notes = []
    melody = m21.stream.Score()
    partFound = False
    for x in self.score:
      # Only add the first part to the melody
      if partFound:
        break
      if not isinstance(x,m21.stream.Part):
        melody.append(x)
      else:
        part = m21.stream.Part()
        melody.append(part)
        partFound = True
        for y in x:
          if not isinstance(y, m21.stream.Measure):
            part.append(y)
          else:
            measure = m21.stream.Measure()
            measure.number = y.number
            part.append(measure)
            for z in y:
              if not isinstance(z, m21.stream.Voice):
                measure.append(z)
              else:
                if not int(z.id) == 1:
                  continue
                else:
                  voice = m21.stream.Voice()
                  voice.id = 1
                  measure.append(voice)
                  for note in z:
                    if not isinstance(note,m21.chord.Chord):
                      voice.append(note)
                    else:
                      pitches = note.sortDiatonicAscending().pitches
                      pitches.reverse()
                      n = m21.note.Note()
                      n.pitch = pitches[0]
                      n.duration = note.duration
                      n.id = note.id
                      voice.append(n)
    return melody

