import database as db
from sequencer import *
from alignment import *
import structure, tools
import scorefeatures as sf
import performancefeatures as pf

s = db.select()
a = Alignment(db.getScore1(s), db.getDeviation1(s))
melodyscore = a.melody()
melody = tools.parseScore(melodyscore)
onset = structure.bestgrouping(melody, structure.second_order_tree(structure.onset, melody, 0.1))
pitch = structure.bestgrouping(melody, structure.second_order_tree(structure.pitch, melody, 0.1))
score = sf.vanDerWeijFeatures(melodyscore, onset) 
performance = pf.vanDerWeijExpression(a, onset)

print score
print performance

