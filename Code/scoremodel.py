import structure, tools, matplotlib
from alignment import *


states = {}
transitions = {}
emissions = {}

# Features: ()

# Take a score as input, return a list of features
def scoremodel(features, expression):
  pitch_positions = [0 for i in range(11)]
  onset_positions = [0 for i in range(11)]
  onset_pos_count = [0 for i in range(11)]
  pitch_pos_count = [0 for i in range(11)]
  for work in list(features.keys()):
    f = features[work]
    e = expression[work]
    for notefeatures, noteexpression in zip(f,e):
      onset_pos_count[int(notefeatures[0])] += 1
      pitch_pos_count[int(notefeatures[1])] += 1
      onset_positions[int(notefeatures[0])] += noteexpression[3]
      pitch_positions[int(notefeatures[1])] += noteexpression[3]
  for i in range(11):
    if onset_pos_count[i] == 0:
      print(i)
      continue
    if pitch_pos_count[i] == 0:
      print(i)
      continue
    onset_positions[i] /= onset_pos_count[i]
    pitch_positions[i] /= pitch_pos_count[i]

  for i in range(11):
    print('Onset: {0}: {1} (Based on {2} examples)'.format(i, onset_positions[i], onset_pos_count[i]))
    print('Pitch: {0}: {1} (Based on {2} examples)'.format(i, pitch_positions[i], pitch_pos_count[i]))

  return (onset_positions, pitch_positions)
#  melody = alignment.melody()
#  groupings = structure.structure(melody)
#  melodynotes = tools.parseScore(melody)
#  features = {}
#  expressive_actions = []
#  for n in melodynotes:
#    features[n.annotation] = features(n)
#    expressive_actions.append(alignment.alignment[n.id, str(n.pitch)])
    


  


