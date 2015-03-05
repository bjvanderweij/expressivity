from structure import *


def repetition(feature, notes, deltas=None):
    if not deltas:
        deltas = deltalist(feature, notes)
    else:
        print(deltas)
    repetition = [0 for i in range(len(deltas))]
    patterns = {}
    for i in range(len(deltas)):
        patterns[str(deltas[i])] = patterns.get(str(deltas[i]), []) + [i]

    for offset in range(1, len(deltas)):
        newpatterns = patterns.copy()
        remove = []
        #print "================="
        #print patterns
        for pattern, indices in patterns.items():
            if len(indices) < 2: continue
            added = []
            for index in indices[:]:
                if index+offset >= len(deltas): continue

                new = ",".join([str(x) for x in deltas[index:index+offset+1]])
                old = ",".join([str(x) for x in deltas[index:index+offset]])
                #print "offset:{2} index:{3} New {0} Old {1}".format(new, old, offset, index)
                if not index in newpatterns.get(new, []):
                    added.append(new)
                    newpatterns[new] = newpatterns.get(new, []) + [index]
                if index in newpatterns.get(old, []) and len(newpatterns[new]) > 1:
                    newpatterns[old].remove(index)
            # Clean up to keep the pattern dictionary small
            for item in added:
                if len(newpatterns[item]) < 2:
                    del newpatterns[item]

        patterns = newpatterns

    for key, value in patterns.items():
        if len(value) > 1:
            if value[0] - 1 > 0:
                p = ",".join([str(x) for x in deltas[value[0]-1:value[0] + len(key.split(","))]])
                if patterns.get(p, []) == [x-1 for x in value]: continue
            for index in value:
                repetition[index] = max(repetition[index], len(key.split(",")))

    #print "Input: {0}".format(deltas)
    #print "Output: {0}".format(repetition)
    repetition = clean_deltalist(repetition)
    #print "Postprocesed output: {0}".format(repetition)
    #repetition.pop(0)
    #repetition.append(0)
    print(repetition)
    return repetition

def clean_deltalist(deltas):
    for i in range(0, len(deltas)):
        current = deltas[i]
        for j in range(i,i+current):
            if(deltas[j] + j > i+current):
                deltas[j] = 0
    return deltas

#def parse(notes, oldprimitives, minlen):
#  primitives = {}
#  i = 0
#  while True:
#    if oldprimitives
#    primitives[notes[i:i+minlen] = primitives.get(notes[i:i+minlen], 0)




def rep_delta_rule(notes, level=None, deltas=None):
    max_delta = max(deltas)
    analyses = []
    lastsplit = 0
    for i in range(1, len(deltas) + 1):
        if deltas[i-1] == max_delta:
            analyses.append(delta_rule(feature, notes[lastsplit:i], deltas[lastsplit:i-1]))
            lastsplit = i
    if lastsplit < len(notes):
        analyses.append(delta_rule(feature, notes[lastsplit:len(notes)], deltas[lastsplit:len(notes)-1]))
    return analyses
