import structure
import database as db
from representation import *

def built(alignment):
  parsetree = structure.parse(alignment.score)
  constituents = structure.groupings(parsetree)
  for constituent in constituents:
    for note in constituent:

