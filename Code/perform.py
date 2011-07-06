from representation import *
from deviations import *
from alignment import *
from analysescore import *
import structure, math



# Expression vector:
#       0       1           2             3           4       5
# E = (ioi_r, loudness_r, articulation, duration_r, ioi_ch, loundness_ch)
def widmerPerform(score, expression, average_loudness=80, tempo=80):
  score.tempo = tempo
  performance = NoteList()
  time = 0
  for i in range(len(score)):
    on = time + structure.ioi(score, i) * math.exp(expression[i][0])
    loudness = average_loudness * math.exp(expression[i][1])
    off = on + structure.duration(score, i) * math.exp(expression[i][3])
    performance.insert(Note(int(on), int(off), score[i].pitch, int(loudness), 0))
    time = on
  return performance

def vanDerWeijPerformSimple(score, melody, segments, expression_vectors, average_loudness=60, bpm=120, converter=NoteList()):
# converter is used to convert milliseconds to ticks and back
  deviations = Deviations()
  deviations.bpm = bpm
  deviations.basedynamics = average_loudness
  tempo_deviations = {}
  alignment = {}

 
  for segment, expression in zip(segments, expression_vectors):
    average_tempo = expression[2]
    for note in segment:
      pointer = note.annotation
      scorepart = melody[pointer[0]]
      scoremeasure = scorepart[pointer[1]]
      scorevoice = scoremeasure[pointer[2]]
      scorenote = scorevoice[pointer[3]]
      measure = scoremeasure.number
      deviations.tempo_deviations[measure, int(scorenote.offset)] = average_tempo

  # Fill in missing deviations
  last = 1.0
  for part in score.parts:
    for measure in part:
      if not isinstance(measure, m21.stream.Measure):
        continue
      deviations.measure_lengths[measure.number] = int(measure.barDuration.quarterLength)
      for beat in range(int(measure.barDuration.quarterLength)):
        if not (measure.number, beat) in deviations.tempo_deviations:
          deviations.tempo_deviations[measure.number, beat] = last
        else:
          last = deviations.tempo_deviations[measure.number, beat]


  for segment, expression in zip(segments, expression_vectors):
    average_relative_loudness = expression[0]
    articulation = expression[1]
    for note in segment:
      pointer = note.annotation
      scorepart = melody[pointer[0]]
      scoremeasure = scorepart[pointer[1]]
      scorevoice = scoremeasure[pointer[2]]
      scorenote = scorevoice[pointer[3]]
      measure = scoremeasure.number
  
      # Articulation is performed duration / note duration
      # The following lines have a problem, if the note has a duration of more than one beat, the expressive
      # tempo for the next beat is not yet defined, expressiveDuration assumes the last known tempo
      # so the damage is light
      duration = converter.microseconds_to_ticks(deviations.getExpressiveDuration(measure, scorenote.offset, scorenote.duration.quarterLength))
      articulated_duration = articulation * float(duration)
      release = (articulated_duration - duration) / converter.microseconds_to_ticks(deviations.getBeatDuration(measure, int(scorenote.offset)))
      alignment[scorenote.id, str(scorenote.pitch)] = [0, release, average_relative_loudness, 0]
  
  a = Alignment(score, deviations, noAlign=True)
  a.alignment = alignment
  a.m = melody
#  toFile(a.m, 'score.txt') 
  return a.melodyPerformance()


def perform(score, melodyscore, onset, expression, dynamics=None, tempo=None, converter=NoteList()):
  if not dynamics:
    dynamics = int(raw_input("Choose base dynamics (somewhere between 50 and 100?) "))
  if not tempo:
    tempo = int(raw_input("Choose base tempo (bpm) "))
  return vanDerWeijPerformSimple(score, melodyscore, onset, expression, dynamics, bpm=tempo, converter=converter)

def vanDerWeijPerform(score, segments, expression_vectors):
  deviations = Deviations()
  tempo_deviations = {}

  for segment, expression in zip(segments, expression_vectors):
    start_tempo = expression[3]
    tempo_direction = expression[5]
    start_loudness = expression[4]
    loudness_direction = expression[6]
    articulation = expression[2]
    i = 0
    beat = 0

    for note in segment:
      velocity = start_loudness + i * loudness_direction

      i += 1
      

  score.tempo = tempo
  performance = NoteList()
  time = 0
  for i in range(len(score)):
    on = time + structure.ioi(score, i) * math.exp(expression[i][0])
    loudness = average_loudness * math.exp(expression[i][1])
    off = on + structure.duration(score, i) * math.exp(expression[i][3])
    performance.insert(Note(int(on), int(off), score[i].pitch, int(loudness), 0))
    time = on
  return performance
