import tools, structure, math

# Least squares fit
def linear_fit(X, Y):
  n = len(X)
  if len(X) != len(Y):
    print "linear fit: WARNING: lengths of data don't match: {0} and {1}".format(len(X), len(Y))
  sum_x=0.0
  sum_y=0.0
  sum_xx=0.0
  sum_xy=0.0
  for x,y in zip(X,Y):
    sum_x=sum_x+x
    sum_y=sum_y+y
    xx=pow(x,2)
    sum_xx=sum_xx+xx
    xy=x*y
    sum_xy=sum_xy+xy

  #Calculating the coefficients
  a=(-sum_x*sum_xy+sum_xx*sum_y)/float(n*sum_xx-sum_x*sum_x)
  b=(-sum_x*sum_y+n*sum_xy)/float(n*sum_xx-sum_x*sum_x)
  return a, b

  #print "The required straight line is Y=%sX+(%s)"%(b,a)



def articulation(notes, i):
  return structure.duration(notes, i)


def vanDerWeijExpression(alignment, segments):
  performance = alignment.expressiveMelody()
  # The two above should be guaranteed to be of equal length.
  # However, better be safe than sorry
  if len(performance) != sum([len(x) for x in segments]):
    print 'This shouldn\'t happen: melodyscore and performance lengths don\'t match: {0} and {1}'.format(len(sum([len(x) for x in segments])), len(performance))
  else:
    print "This is good, performance length and score length match"
  
  expression = []
  i = 0
  index = 0
  for segment in segments:
    length = float(len(segment))
    # Segments can't have a length of 1, the features don't work then
    if length <=1:
      print "WARNING: Don't know how to deal with atomic constituent, skipping, solve this!"
      continue
    average_articulation = 0
    tempos = []
    for note in segment:
      pointer = note.annotation
      scorepart = alignment.melody()[pointer[0]]
      scoremeasure = scorepart[pointer[1]]
      scorevoice = scoremeasure[pointer[2]]
      scorenote = scorevoice[pointer[3]]
      measure = scoremeasure.number
      
      tempo = alignment.deviations.tempo_deviations[measure, int(scorenote.offset)]
      if not tempo in tempos:
        tempos.append(tempo)

      # Find out if the next note is a rest, if so use the ratio between expressive duration and duration
      useScoreDuration = False
      # Last note of this
      if pointer[3] + 1 == len(scorevoice):
        if pointer[1] + 1 == len(scorepart):
          useScoreDuration = True
        elif scorepart[pointer[1]+1].getElementById(scorevoice.id).notes[0].isRest:
          measure = scorepart[pointer[1]+1]
          useScoreDuration = True
      elif scorevoice[pointer[3]+1].isRest:
        useScoreDuration = True

      ioi = 1
      if useScoreDuration:
        ioi = alignment.deviations.getExpressiveDuration(scoremeasure.number, scorenote.offset, scorenote.duration.quarterLength)
      else: ioi = structure.ioi(performance, index)

      average_articulation += 1/length * structure.duration(performance, index) / ioi 
      index += 1

    note_onsets = [n.on for n in segment]

    # Calculate performance parameters/features
    average_ioi_ratio = sum([1/length * articulation(segment, j) for j in range(int(length))] )
    (start_loudness, loudness_direction) = linear_fit(note_onsets, [x.onvelocity for x in segment])
    average_tempo = tempo / length
    (start_tempo, tempo_direction) = linear_fit(range(len(tempos)), tempos)
    average_loudness = sum([1/length * x.onvelocity for x in segment])

    expression.append((average_ioi_ratio, average_loudness, average_articulation, start_tempo, start_loudness, tempo_direction, loudness_direction))
    i += 1

  return expression

def expressionWidmer(alignment):
  performance = alignment.expressiveMelody()
  melodyscore = alignment.melody()
  score = tools.parseScore(melodyscore)
  # The two above should be guaranteed to be of equal length.
  # However, better be safe than sorry
  if len(performance) != len(score):
    print 'This shouldn\'t happen: melodyscore and performance lengths don\'t match: {0} and {1}'.format(len(score), len(performance))
  else:
    print "This is good, performance length and score length match"
  
  # Mean loudness
  mean_l = 0.0
  for note in performance:
    mean_l += note.onvelocity

  mean_l = mean_l / float(len(performance))

  expression = []
  lasttempo = float(alignment.deviations.bpm)
  lastdynamics = mean_l
 
  # Assume same note order in score and performance (am I being naive?)
  for i in range(len(performance)):
    ioi_ratio = math.log(structure.ioi(performance, i) / float(structure.ioi(score, i)))
    loudness_ratio = math.log(performance[i].onvelocity / mean_l)
    
    # This obviously results in zero divisions
    #articulation = math.log(structure.silence(performance, i) / float(structure.silence(score, i))) 
    articulation = 0

    if(structure.duration(performance, i) < 1):
      print "Invalid performance note :( skipping"
      continue
    duration_ratio = math.log(structure.duration(performance, i) / float(structure.duration(score, i)))

    # To be implemented: second order ioi loudness and articulation
    ioi_change = 0
    loudness_change = 0
    articulation_change = 0
    
    # E = (ioi_r, loudness_r, articulation, duration_r, ioi_ch, loundess_ch)
    e = (ioi_ratio, loudness_ratio, articulation, duration_ratio, ioi_change, loudness_change)
    expression.append(e)


  return expression


def expressionOLD(alignment):

  melody = tools.parseScore(melodyscore)
  lastnote = None
  lastscorenote = None

  mean_vel = 0.0
  skipped = 0
  for note in melody:
    scoreindex = note.annotation
    scorenote = melodyscore[scoreindex[0]][scoreindex[1]][scoreindex[2]][scoreindex[3]]
    deviation = alignment.alignment[scorenote.id, str(scorenote.pitch)]
    if not deviation:
      skipped += 1
      continue
    mean_vel += deviation[2] * 100.0

  mean_vel = mean_vel / float(len(melody) - skipped)

  expression = []
  lasttempo = float(alignment.deviations.bpm)
  lastdynamics = mean_vel
  lastdeviation = (0, 0, 1, 1)
  for note in melody:
    scoreindex = note.annotation
    scorenote = melodyscore[scoreindex[0]][scoreindex[1]][scoreindex[2]][scoreindex[3]]
    measure = melodyscore[scoreindex[0]][scoreindex[1]].number
    
    deviation = alignment.alignment[scorenote.id, str(scorenote.pitch)]

    if not deviation:
      deviation = lastdeviation
    attack = deviation[0]
    release = deviation[1]
    dynamics = deviation[2]
    relative_dynamics = dynamics * 100.0 / lastdynamics

    if (measure, int(scorenote.offset)) in alignment.deviations.tempo_deviations:
      tempo = alignment.deviations.tempo_deviations[measure, int(scorenote.offset)] * alignment.deviations.bpm
    else:
      print "{0} {1} not found in tempo deviations".format(measure, int(scorenote.offset))
      tempo = lasttempo
    relative_tempo = tempo / lasttempo
    lasttempo = tempo
    lastdynamics = dynamics * 100.0
    expression.append((attack, release, dynamics, math.log(relative_tempo), math.log(relative_dynamics)))

    lastnote = note
    lastscorenote = scorenote
    lastdeviation = deviation
  return expression

