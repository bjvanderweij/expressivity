import database as db
from alignment import *
from representation import *
from sequencer import *
from score import *

selection = db.select()
alignment = Alignment(db.getScorePath1(selection), db.getDeviation1(selection))
seq = Sequencer()
seq.play(alignment.expressiveMelody())
#s = Score(alignment.score, alignment)


