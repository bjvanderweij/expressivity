import database as db
from alignment import *
from representation import *
import structure, tools, scorefeatures, performancefeatures


def trainset(composers=None, pianist=None):
  queries = []
  if not composers:
    composers = db.composers
  for composer in composers:
    works = db.getWorks(composer)
    for work in works:
      if pianist:
        if work[1] == pianist:
          queries.append((composer, work[0], work[1], work[2]))
      else:
        queries.append((composer, work[0], work[1], work[2]))
  return queries


def train(trainset):
  expression = {}
  features = {}
  print ">>>Loading scores and deviations, this will take hours and may eat all you memory"
  for query in trainset:
    print ">>>Loading: {0}".format(query)
    score = db.getScore1(query)
    deviations = db.getDeviation1(query)
    alignment = Alignment(score, deviations)
    melody = alignment.melody()
    segments = structure.groupings(structure.list_to_tree(structure.first_order_tree(structure.onset, tools.parseScore(melody), 0)), 1)
    expression[query] = performancefeatures.vanDerWeijExpression(alignment, segments)
    features[query] = scorefeatures.vanDerWeijFeatures(melody, segments)


  tools.saveFeatures(features, expression)
#  tools.saveCSV(features, expression)

if __name__ == "__main__":
  import sys
  train(trainset(sys.argv[1:]))


