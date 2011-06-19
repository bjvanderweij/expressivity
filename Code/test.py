import database as db
from alignment import *
from representation import *
from sequencer import *
from score import *
import tools, structure

selection = db.select()
score = Score(db.getScore1(selection))
melody = score.melody()
notes = tools.parseScore(melody)
s1 = structure.delta_rule(structure.pitch, notes[:])
print "PITCH DELTA TREE"
print tools.recursive_print(s1) 
s2 = structure.delta_rule(structure.onset, notes[:])
print "IOI DELTA TREE"
print tools.recursive_print(s2) 
struct = structure.combine(s1, s2)
print "COMBINED DELTA TREES"
print tools.recursive_print(struct) 
#print ','.join([n.name() for n in notes])
seq = Sequencer()
seq.play(notes)
#s = Score(alignment.score, alignment)


