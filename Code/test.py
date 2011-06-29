import database as db
from alignment import *

s = db.select()
a = Alignment(db.getScore1(s), db.getDeviation1(s))
p = a.performance()
