import database as db
from alignment import *
from representation import *
from sequencer import *
from score import *
import tools, structure, sys

if len(sys.argv) > 1:
  deltas = structure.repetition(None, None, sys.argv[1])
  print deltas
  s3 = structure.delta_rule(None, 's'+sys.argv[1], deltas)
  print tools.recursive_print(s3)
  sys.exit(0)
selection = db.select()
score = Score(db.getScore1(selection))
melody = score.melody()
notes = tools.parseScore(melody)
deltas = []

print "COMBINED DELTA TREES"

def avg_list(lists, weights=None):
  sumlist = []
  if not weights:
    weights = [1 for i in range(len(lists))]
  for l in range(len(lists)):
    index = 0
    for item in lists[l]:
      if index + 1 > len(sumlist):
        sumlist.append(item)
      else:
        sumlist[index] += weights[l] * item
      index += 1
  result = []
  for item in sumlist:
    result.append(item / float(len(lists)))
  return result

def normalize(l):
  m = float(max(l))
  result = []
  if(m == 0): 
    m = 1
  for i in l:
    result.append(i/m)
  return result

def square(l):
  result = []
  for i in l:
    result.append(i*i)
  return result

def preprocess(l):
  return normalize(square(l))


#for feature in [structure.pitch, structure.onset]:
#  deltas.append(normalize(structure.repetition(feature, notes)))

for feature in [structure.onset, structure.pitch]:
  deltas.append(preprocess(structure.deltalist(feature, notes)))  

avg = avg_list(deltas, [2, 1])
s3 = structure.delta_rule(None, notes, avg)
#avg = avg_list(repdeltas)
#rep = structure.delta_rule(None, notes, avg)
print tools.recursive_print(s3)
#print "REPETITION DELTA:"
#print tools.recursive_print(rep)

for i in range(15):
  groups = structure.groupings(structure.list_to_tree(s3), i)
  avg_group = 0
  for group in groups:
    avg_group += len(group)
  avg_group /= float(len(groups))
  print "Level {0}. Notes to groups ratio: {1}, average group size: {2}".format(i, len(groups)/float(len(notes)), avg_group)
  if len(groups)/float(len(notes)) == 1: break

print "Choose level"
level = int(raw_input(""))
groups = structure.groupings(structure.list_to_tree(s3), level)
  
structured_notes = []
loud = False
for group in groups:
  if loud:
    loud = False
  else:
    loud = True
  for leaf in group:
    if loud:
      leaf.contents.onvelocity = 100
    else:
      leaf.contents.onvelocity = 50
    structured_notes.append(leaf.contents)
  

namelist = []
for group in groups:
  namelist.append([leaf.contents.name() for leaf in group])
print namelist

notes.notes = structured_notes
#print tools.recursive_print(struct) 
#print ','.join([n.name() for n in notes])
seq = Sequencer()
seq.play(notes)
#s = Score(alignment.score, alignment)


