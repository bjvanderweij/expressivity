import database as db
from alignment import *
from representation import *
from sequencer import *
from score import *
import tools

selection = db.select()
score = db.getScore1(selection)
notes = tools.parseScore(score)
seq = Sequencer()
seq.play(notes)
#s = Score(alignment.score, alignment)
