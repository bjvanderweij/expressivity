import database as db
from sequencer import *
from alignment import *
import structure, tools
import scorefeatures as sf
import performancefeatures as pf
import perform

s = db.select()
a = Alignment(db.getScore1(s), db.getDeviation1(s))
melodyscore = a.melody()
melody = tools.parseScore(melodyscore)
onset = structure.groupings(structure.list_to_tree(structure.first_order_tree(structure.onset, melody, 0.1)), 1)
score = sf.vanDerWeijFeatures(melodyscore, onset) 
performance = pf.vanDerWeijExpression(a, onset)

print(score)
print(performance)

seq = Sequencer()
seq.play(perform.vanDerWeijPerformSimple(a.score, melodyscore, onset, performance, bpm=a.deviations.bpm, converter=melody))

