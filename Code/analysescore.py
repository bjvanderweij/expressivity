import music21 as m21
import sys


def analyse(score):
  recursive_score(score[1][0:4], 0)
  recursive_score(score[2][0:4], 0)

def toText(score):
  recursive_score(score, 0)

def toFile(score, f):
  out = open(f, 'w')
  recursive_score(score, 0, out)
  out.close()

def recursive_score(obj, level, out=None):
  string = ''
  for tab in range(0,level):
    string += '\t'
#  if isinstance(obj, m21.note.Note):
#    print obj.measureNumber

  line = '{0}{1} {2} [duration:{3}]'.format(string, str(obj), obj.offset, str(obj.duration.quarterLength)) 
  if out:
    out.write(line + '\n')
  else:
    print(line)
  if hasattr(obj,'__iter__'):
    for x in obj:
      recursive_score(x, level + 1, out)

if __name__ == "__main__":
  toText(m21.converter.parse(sys.argv[1]))
