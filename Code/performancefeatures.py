import tools, structure, math

def expression(alignment):
  performance = alignment.expressiveMelody()
  melodyscore = alignment.melody()
  score = tools.parseScore(melodyscore)
  # Tied notes end up as zero length notes here, clean this mess up
  print 'SCORE LENGTH: {0}'.format(len(score))
  remove = []
  for i in range(len(score)):
    if structure.duration(score, i) == 0:
      remove.append(score[i])
  for n in remove:
    score.remove(n)
  print 'SCORE LENGTH: {0}'.format(len(score))
  # The two above should be guaranteed to be of equal length.
  # However, better be safe than sorry
  if len(performance) != len(score):
    print 'This shouldn\'t happen: melodyscore and performance lengths don\'t match: {0} and {1}'.format(len(performance), len(score))
  
  # Mean loudness
  mean_l = 0.0
  for note in performance:
    mean_l += note.onvelocity

  mean_l = mean_l / float(len(performance))
  print "Average loudness: {0}".format(mean_l)

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

