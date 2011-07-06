import tools, structure, math
import performancefeatures as pf


# Take a score, split it in melody and harmony, do structure analysis and output features per note.

def pitch_interval(notes, i):
  if i == 0: return 0
  return notes[i].pitch - notes[i-1].pitch

def duration_ratio(notes, i):
  if i == 0: return 1
  return math.log((notes[i].off - notes[i].on) / float(notes[i-1].off - notes[i-1].on))

def vanDerWeijFeatures(melodyscore, segments):
  # This is radically different, we only look at features at constituent level
  melody = tools.parseScore(melodyscore)

  features = []
  index = 0
  for i in range(len(segments)):
    length = len(segments[i]) 
    # Calculate averages:
    # What if the segment is len 1?
    pitch_int = structure.bare_deltalist(structure.pitch, segments[i])
    abs_pitch_int = structure.absolute_deltalist(structure.pitch, segments[i])
    dPitch = 1/float(length) * sum(pitch_int)
    abs_dPitch = 1/float(length) * sum(abs_pitch_int)
    dDuration = 1/float(length) * sum(structure.bare_deltalist(structure.duration, segments[i]))
    abs_dDuration = 1/float(length) * sum(structure.absolute_deltalist(structure.duration, segments[i]))
    silence = 1/float(length) * sum([structure.silence(segments[i], j+1) for j in range(len(segments[i])-1)])
    ddPitch = 1/float(length) * sum(structure.second_order_deltalist(pitch_int))
    abs_ddPitch = 1/float(length) * sum(structure.second_order_deltalist(abs_pitch_int))
    
    #print [structure.silence(segments[i], j) for j in range(len(segments[i]))]

    onsets = structure.normalize([n.on for n in segments[i]])
    pitches = structure.normalize([n.pitch for n in segments[i]])
    if len(onsets) == 1:
      pitch_direction = 0
    else:
      pitch_direction = pf.linear_fit(onsets, pitches)[1]

    # Average of deltafunctions?
    # Average of second order deltafunctions?
    # Average of log relatives?
    # Polyfonie
    features.append((dPitch, abs_dPitch, dDuration, abs_dDuration, silence, ddPitch, abs_ddPitch, pitch_direction))

  return features
    

# [onset arch, pitch arch, pitch_interval, duration_ratio]
def widmerFeatures(melodyscore):
  melody = tools.parseScore(melodyscore)
  onset_segments = structure.bestgrouping(melody, structure.second_order_tree(structure.onset, melody, 0.1))
  pitch_segments = structure.bestgrouping(melody, structure.second_order_tree(structure.pitch, melody, 0.1))
  features = [[] for i in range(len(melody))]

  index = 0
  for i in range(len(onset_segments)):
    start = onset_segments[i][0].on
    end = onset_segments[i][len(onset_segments[i])-1].off
    length = float(end - start)
    if not i+1 >= len(onset_segments):
      end = onset_segments[i+1][0].on
    
    for note in onset_segments[i]:
      nearest_border = min(end - note.on, note.on - start)
      features[index] = [nearest_border]
      index += 1

  index = 0
  for i in range(len(pitch_segments)):
    start = pitch_segments[i][0].on
    end = pitch_segments[i][len(pitch_segments[i])-1].off
    length = float(end - start)
    if not i+1 >= len(pitch_segments):
      end = pitch_segments[i+1][0].on
    
    for note in pitch_segments[i]:
      nearest_border = min(end - note.on, note.on - start)
      features[index].append(nearest_border)
      index += 1

  for i in range(len(melody)):
    features[i].append(pitch_interval(melody, i))
    features[i].append(duration_ratio(melody, i))
  print features[10]
  return features

# [onset_pos, pitch_pos, pitch_interval, duration_ratio]
def features1(melodyscore):
  melody = tools.parseScore(melodyscore)
  onset_segments = structure.bestgrouping(melody, structure.second_order_tree(structure.onset, melody, 0.1))
  pitch_segments = structure.bestgrouping(melody, structure.second_order_tree(structure.pitch, melody, 0.1))
  features = [[] for i in range(len(melody))]

  index = 0
  for i in range(len(onset_segments)):
    start = onset_segments[i][0].on
    end = onset_segments[i][len(onset_segments[i])-1].off
    length = float(end - start)
    if not i+1 >= len(onset_segments):
      end = onset_segments[i+1][0].on
    
    for note in onset_segments[i]:
      pos = note.on - start
      rel_pos = discretize(0, 1, pos / length, 10)
      features[index] = [rel_pos]
      index += 1

  index = 0
  for i in range(len(pitch_segments)):
    start = pitch_segments[i][0].on
    end = pitch_segments[i][len(pitch_segments[i])-1].off
    length = float(end - start)
    if not i+1 >= len(pitch_segments):
      end = pitch_segments[i+1][0].on
    
    for note in pitch_segments[i]:
      pos = note.on - start
      rel_pos = discretize(0, 1, pos / length, 10)
      features[index].append(rel_pos)
      index += 1

  for i in range(len(melody)):
    features[i].append(pitch_interval(melody, i))
    features[i].append(duration_ratio(melody, i))

  return features
    
