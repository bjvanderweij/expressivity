import tools
import database as db
import random, sys
from score import *

selections = []

amount = 2

store_xml = False

if len(sys.argv) > 1:
  if sys.argv[1] == 'xml':
    store_xml = True

print "Making selection"

for composer in db.composers:
  works = db.getWorks(composer)
  for i in range(amount):
    work = random.choice(works)
    works.remove(work)
    if len(works ) == 0: break
    selections.append((composer, work[0], work[1], work[2]))

print "Storing melodies"

for selection in selections:
  score = Score(db.getScore1(selection))
  if store_xml:
    tools.saveXML(score.melody(), '_'.join(score.score.metadata.title.split(" ")))
  else:
    tools.savePDF(score.melody(), '_'.join(score.score.metadata.title.split(" ")))

