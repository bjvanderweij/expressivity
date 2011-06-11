import music21 as m21


def analyse(score):
  recursive_score(score[1][0:4], 0)
  recursive_score(score[2][0:4], 0)

def recursive_score(obj, level):
  string = ''
  for tab in range(0,level):
    string += '\t'
  print string + str(obj)
  if hasattr(obj,'__iter__'):
    for x in obj:
      recursive_score(x, level + 1)


