import tools, structure, math


# Take a score, split it in melody and harmony, do structure analysis and output features per note.

def discretize(min, max, value, bins=10):
  if value < min or value > max:
    print "Discretize error: value outside range, returning 0"
    return 0
  return int((value - min) * (bins / float(max - min)))

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
    abs_interval = 1/float(length) * sum([structure.absolute_delta(segments[i], structure.pitch, x) for x in range(1, length)])
    duration = 1/float(length) * sum([structure.duration(segments[i], x) for x in range(length)])
    pitch = 1/float(length) * sum([structure.pitch(segments[i], x) for x in range(length)])
    pitch_direction = (segments[i][length-1].pitch - segments[i][0].pitch ) / float(length)
    # Average of deltafunctions?
    # Average of second order deltafunctions?
    # Average of log relatives?
    features.append((pitch, duration, abs_interval, pitch_direction))

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
    
