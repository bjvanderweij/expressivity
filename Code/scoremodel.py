import structure, tools
from alignment import *


# Take a score as input, return a list of features
def scoremodel(alignment):
  melody = alignment.melody()
  groupings = structure.structure(melody)
  melodynotes = tools.parseScore(melody)
  features = {}
  expressive_actions = []
  for n in melodynotes:
    features[n.annotation] = features(n)
    expressive_actions.append(alignment.alignment[n.id, str(n.pitch)])
    

def features(note):
  # dummy feature
  return (n.pitch)

    

  


