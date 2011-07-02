from alignment import *
from score import *
from music21 import *
from trees import *


def onset(notes, i):
  return notes[i].on

def offset(notes, i):
  return notes[i].off

def pitch(notes, i):
  return notes[i].pitch

def loudness(notes, i):
  return notes[i].onvelocity

def duration(notes, i):
  return notes[i].off - notes[i].on

def virtual_silence(notes, i):
  if i >= len(notes) - 1:
    return 0
  return notes[i+1].on - notes[i].off

def virtual_duration(notes, i):
  # This is not what Markwin suggests, the last notes' vd should be larger
  if i >= len(notes) - 1:
    return duration(notes, len(notes)-1) 
  return notes[i+1].on - notes[i].on

features = [onset, offset, pitch, loudness, duration, virtual_duration]

def silence(notes, i, tolerance=1):
  delta = notes[i].on - notes[i-1].off
  return delta

def ioi(notes, i):
  if i == 0:
    return 1
  return bare_delta(notes, onset, i)

def bare_delta(notes, feature, i, tolerance=1):
  if feature == silence:
    return silence(notes, i, tolerance)
  else:
    delta = feature(notes, i) - feature(notes, i-1)
    return delta


# Perhaps stochastic tolerance will work better?
def absolute_delta(notes, feature, i, tolerance=1):
  return abs(bare_delta(notes, feature, i, tolerance))

def relative_delta(notes, feature, i, depth=4, tolerance=1):
  avg_delta = 0
  for x in range(1, depth+1):
    if i-x <= 0: break
    avg_delta += absolute_delta(notes, feature, i-x, tolerance)
  if i == 1:
    return 0
  elif i <= depth:
    avg_delta /= float(i-1)
  else: 
    avg_delta /= float(depth)
  if avg_delta == 0: return 0
  return abs(float(absolute_delta(notes, feature, i, tolerance)) - avg_delta)

def relative_deltalist(feature, notes):
    return [relative_delta(notes, feature, i) for i in range(1, len(notes))]

def absolute_deltalist(feature, notes):
    return [absolute_delta(notes, feature, i) for i in range(1, len(notes))]

def second_order_deltalist(deltas):
    result = []
    for i in range(1, len(deltas)):
      result.append(abs(deltas[i] - deltas[i-1]))
    return result

def deltarule(notes, deltas, splittolerance=0):
  if len(notes) == 1:
    return notes[0]
  max_delta = max(deltas)
  analyses = []
  lastsplit = 0
  for i in range(1, len(deltas) + 1):
    if deltas[i-1] >= max_delta - splittolerance and deltas[i-1] <= max_delta + splittolerance:
    #if deltas[i-1] == max_delta:
      analyses.append(deltarule(notes[lastsplit:i], deltas[lastsplit:i-1], splittolerance))
      lastsplit = i
  if lastsplit < len(notes):
    analyses.append(deltarule(notes[lastsplit:len(notes)], deltas[lastsplit:len(notes)-1], splittolerance))
  return analyses

def second_order_deltarule(notes, deltas, splittolerance=0, rec=0):
  #if rec > 5: return
  if len(notes) <= 2:
    if len(deltas) == 1 and deltas[0] > 0:
      return [notes[0], notes[1]]
    return notes
  max_delta = max(deltas)
  if max_delta == 0:
    return notes
  analyses = []
  lastsplit = 0
  lastdeltasplit = 0 
#  print [n for n in notes]
#  print deltas
  for i in range(len(deltas)):
    if deltas[i] >= max_delta - splittolerance and deltas[i] <= max_delta + splittolerance:
      analyses.append(second_order_deltarule(notes[lastsplit:i+1], deltas[lastdeltasplit:i], splittolerance, rec+1))
      lastsplit = i+1
      lastdeltasplit = i+1
#      print "lennotes: {2} lendeltas: {3}, split {0}, deltasplit {1}".format(lastsplit, lastdeltasplit, len(notes), len(deltas))
  if lastsplit < len(notes):
    analyses.append(second_order_deltarule(notes[lastsplit:len(notes)], deltas[lastdeltasplit:len(deltas)], splittolerance, rec+1))
  return analyses

def list_to_tree(l):
  if hasattr(l,'__iter__'):
    return Node([list_to_tree(child) for child in l])
  else:
    return Leaf(l)

def tree_to_list(t):
  if isinstance(t,Node):
    return [tree_to_list(child) for child in t]
  else:
    return t.contents


def subset(x, y):
  for i in x:
    if not i in y:
      return False
  return True

def find_multinodes(trees):
  for tree in trees:
    pass
    


def combine(a, b):
  result = []
  print a, b
  if isinstance(a,Node):
    for x in a:
      for y in b:
        if yield_equal([x,y]):
          return MultiNode([x,y])
    else:
      result = a
  else:
    return None
  return result

def leaf_nodes(node):
  leafs = []
  if isinstance(node,Node):
    for child in node:
      leafs += leaf_nodes(child) 
  else:
    leafs = [node]
  return leafs

def yield_equal(nodes):
  if nodes == []: return False
  leafs = leaf_nodes(nodes[0])
  for node in nodes:
    if leaf_nodes(node) != leafs:
      return False
  return True

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

def get_level(tree, level, currentlevel):
  if level == currentlevel:
    return [tree]
  if isinstance(tree, Node):
    result = []
    for node in tree.children:
      nodes = get_level(node, level, currentlevel + 1)
      if(nodes):
        result += nodes
      else:
        result += [Node([leaf]) for leaf in leaf_nodes(node)]
    return result
  return None

def groupings(tree, level):
  nodes = get_level(tree, level, 0)
  groups = []
  for node in nodes:
    groups.append([leaf.contents for leaf in leaf_nodes(node)])
  return groups

# Lousy criterium for selecting a particular grouping from a tree
def bestgrouping(melody, tree):
  for i in range(10):
    groups = groupings(list_to_tree(tree), i)
    avg_group = 0
    for group in groups:
      avg_group += len(group)
    avg_group /= float(len(groups))
    if  avg_group < len(melody) / 4.0:
      return groups

def first_order_tree(feature, notes, tolerance=0):
  delta = absolute_deltalist(feature, notes)
  return deltarule(notes, delta, tolerance)

def second_order_tree(feature, notes, tolerance=0):
  delta = absolute_deltalist(feature, notes)
  sodelta = normalize(second_order_deltalist(delta))
  return second_order_deltarule(notes, sodelta, tolerance)

if __name__ == '__main__':
  import database as db
  import tools
  w = db.select()
  score = Score(db.getScore1(w))
  melodyscore = score.melody()
  melody = tools.parseScore(melodyscore)
  trees = [second_order_tree(onset, melody, 0.0), second_order_tree(pitch, melody, 0.0), first_order_tree(onset, melody, 0.0), first_order_tree(pitch, melody)]

  for tree in trees:
    print "Tree"
    print tools.recursive_print(tree)
    
  
  for i in range(5):
    for j in range(len(trees)):
      groups = groupings(list_to_tree(trees[j]), i)
      avg_group = 0
      for group in groups:
        avg_group += len(group)
      avg_group /= float(len(groups))
      print "Tree: {0} Level {1} group size {2}".format(j, i, avg_group)
    print '------------------'
    if len(groups)/float(len(melody)) == 1: break

  print "Choose level"
  level = int(raw_input(""))
  print "Choose tree"
  tree = int(raw_input(''))
  groups = groupings(list_to_tree(trees[tree]), level)
  structured_notes = []
  loud = False
  for group in groups:
    if loud:
      loud = False
    else:
      loud = True
    for leaf in group:
      if loud:
        leaf.onvelocity = 80
      else:
        leaf.onvelocity = 50
      structured_notes.append(leaf)

  namelist = []
  for group in groups:
    namelist.append([leaf.name() for leaf in group])
  print namelist

  melody.notes = structured_notes
  from sequencer import *
  seq = Sequencer()
  seq.play(melody)
  