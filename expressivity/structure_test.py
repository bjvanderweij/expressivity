import database as db
from alignment import *
from representation import *
from sequencer import *
from score import *
import tools, structure, sys
import matplotlib.pyplot as plt


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

if len(sys.argv) > 1:
    notes = sys.argv[1]
    deltas = [int(x) for x in sys.argv[2]]
    s3 = structure.second_order_deltarule(notes, deltas, 0)
    print(tools.recursive_print(s3))
    sys.exit(0)


selection = db.select()
score = Score(db.getScore1(selection).stripTies())
melody = score.melody()
notes = tools.parseScore(melody)
deltas = []


print("COMBINED DELTA TREES")
#for feature in [structure.pitch, structure.onset]:
#  deltas.append(normalize(structure.repetition(feature, notes)))

for feature in [structure.onset, structure.duration, structure.pitch]:
    print(">>>> {0} absolute:".format(feature))
    print(structure.absolute_deltalist(feature, notes))
    print(">>>> {0} relative:".format(feature))
    print(structure.relative_deltalist(feature, notes))


#deltas.append(normalize(square(structure.absolute_deltalist(structure.onset, notes))))
#deltas.append(normalize(structure.relative_deltalist(structure.pitch, notes)))

deltas = []
deltas.append(structure.absolute_deltalist(structure.onset, notes))
deltas.append(square(structure.absolute_deltalist(structure.pitch, notes)))

sodeltas = []
sodeltas.append(normalize(structure.second_order_deltalist(deltas[0])))
sodeltas.append(normalize(structure.second_order_deltalist(deltas[1])))


#fig = plt.figure()
#dplot = fig.add_subplot(111)
#sodplot = fig.add_subplot(111)
#dplot.plot([i for i in range(len(deltas[0]))], deltas[0])
#sodplot.plot([i for i in range(len(sodeltas[0]))], sodeltas[0])
#plt.show()

avg = normalize(avg_list(sodeltas, [1, 1]))

s = []
s.append(structure.second_order_deltarule(notes, sodeltas[0], 0.1))
s.append(structure.second_order_deltarule(notes, sodeltas[1], 0.1))
s.append(structure.second_order_deltarule(notes, avg, 0.1))
#s3 = structure.delta_rule(notes, avg, 0.1)
#avg = avg_list(repdeltas)
#rep = structure.delta_rule(None, notes, avg)
print(tools.recursive_print(s[0]))
print(tools.recursive_print(s[1]))
print(tools.recursive_print(s[2]))

#print "REPETITION DELTA:"
#print tools.recursive_print(rep)

for i in range(5):
    groups = structure.groupings(structure.list_to_tree(s[0]), i)
    avg_group = 0
    for group in groups:
        avg_group += len(group)
    avg_group /= float(len(groups))
    print("ONSET: Level {0}, average group size: {1}".format(i, avg_group))
    groups = structure.groupings(structure.list_to_tree(s[1]), i)
    avg_group = 0
    for group in groups:
        avg_group += len(group)
    avg_group /= float(len(groups))
    print("PITCH: Level {0}, average group size: {1}".format(i, avg_group))
    groups = structure.groupings(structure.list_to_tree(s[2]), i)
    avg_group = 0
    for group in groups:
        avg_group += len(group)
    avg_group /= float(len(groups))
    print("COMBINED: Level {0}, average group size: {1}".format(i, avg_group))
    if len(groups)/float(len(notes)) == 1: break

print("Choose level")
level = int(input(""))
print("Choose tree")
tree = int(input(''))
groups = structure.groupings(structure.list_to_tree(s[tree]), level)

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
print(namelist)

notes.notes = structured_notes
#print tools.recursive_print(struct)
#print ','.join([n.name() for n in notes])
seq = Sequencer()
seq.play(notes)
#s = Score(alignment.score, alignment)
