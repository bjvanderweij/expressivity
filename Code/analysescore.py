import music21 as m21
import sys


def analyse(score):
  recursive_score(score[1][0:4], 0)
  recursive_score(score[2][0:4], 0)

def toText(score):
  recursive_score(score, 0)

def recursive_score(obj, level):
  string = ''
  for tab in range(0,level):
    string += '\t'
  print '{0}{1} [duration:{2}]'.format(string, str(obj), str(obj.duration)) 
  if hasattr(obj,'__iter__'):
    for x in obj:
      recursive_score(x, level + 1)

if __name__ == "__main__":
  toText(m21.converter.parse(sys.argv[1]))
